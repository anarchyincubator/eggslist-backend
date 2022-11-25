import stripe
from django.conf import settings
from django.db.utils import IntegrityError

from eggslist.store.models import ProductArticle
from eggslist.users.models import User, UserStripeConnection


def create_account(user: User) -> tuple[stripe.Account, UserStripeConnection]:
    account = stripe.Account.create(
        type=settings.STRIPE_SELLERS_ACCOUNT_TYPE,
        email=user.email,
        metadata={"user.id": user.id},
    )
    try:
        user_stripe_connection = UserStripeConnection.objects.create(
            user=user, stripe_account=account.stripe_id
        )
    except IntegrityError:
        UserStripeConnection.objects.filter(user=user).delete()
        user_stripe_connection = UserStripeConnection.objects.create(
            user=user, stripe_account=account.stripe_id
        )
    return account, user_stripe_connection


def create_connect_url(stripe_connection: UserStripeConnection) -> str:
    connect_link = None
    try:
        connect_link = stripe.AccountLink.create(
            account=stripe_connection.stripe_account,
            refresh_url=f"{settings.SITE_URL}/{settings.STRIPE_CONNECT_REFRESH_URL}",
            return_url=f"{settings.SITE_URL}/{settings.STRIPE_CONNECT_RETURN_URL}",
            type="account_onboarding",
        )
    except stripe.error.InvalidRequestError as e:
        if "No such account" in e.user_message:
            account, user_stripe_connection_model = create_account(stripe_connection.user)
            connect_link = stripe.AccountLink.create(
                account=user_stripe_connection_model.stripe_account,
                refresh_url=f"{settings.SITE_URL}/{settings.STRIPE_CONNECT_REFRESH_URL}",
                return_url=f"{settings.SITE_URL}/{settings.STRIPE_CONNECT_RETURN_URL}",
                type="account_onboarding",
            )
    if connect_link is None:
        raise ConnectionError("There is no connection link")
    return connect_link.url


def is_onboarding_completed(stripe_connection: UserStripeConnection) -> bool:
    account = stripe.Account.retrieve(stripe_connection.stripe_account)
    return account.details_submitted


def create_purchase_url(
    customer: User,
    seller_connection: UserStripeConnection,
    product: ProductArticle,
    transaction_id: int,
) -> str:
    checkout_details = {
        "line_items": [
            {
                "quantity": 1,
                "price_data": {
                    "currency": "USD",
                    "product_data": {
                        "name": product.title,
                        "description": product.description,
                        "images": [product.image.url],
                    },
                    "unit_amount": int(float(product.price) * 100),  # Cents
                },
            }
        ],
        "mode": "payment",
        "success_url": f"{settings.SITE_URL}/{settings.STRIPE_TRANSACTION_SUCCESS_URL}",
        "cancel_url": f"{settings.SITE_URL}/{settings.STRIPE_TRANSACTION_CANCEL_URL}",
        "payment_intent_data": {"application_fee_amount": settings.STRIPE_COMMISSION_FEE},
        "stripe_account": seller_connection.stripe_account,
        "client_reference_id": str(transaction_id),
        "metadata": {"transaction_id": str(transaction_id)},
    }

    if customer.is_authenticated and customer.email:
        checkout_details["customer_email"] = customer.email

    session = stripe.checkout.Session.create(**checkout_details)

    return session.url
