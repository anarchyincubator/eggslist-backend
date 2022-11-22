import stripe
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.log import request_logger
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.store.models import Transaction
from eggslist.users.models import UserStripeConnection
from eggslist.utils.emailing import send_mailing

SESSION_TRANSACTION_EVENT_TO_STATUS = {
    "checkout.session.completed": Transaction.Status.CHECKOUT_COMPLETED,
    "checkout.session.async_payment_succeeded": Transaction.Status.SUCCESS,
    "checkout.session.async_payment_failed": Transaction.Status.FAILED,
    "checkout.session.expired": Transaction.Status.FAILED,
}

PAYMENT_INTENT_TRANSACTION_EVENT_TO_STATUS = {
    "payment_intent.canceled": Transaction.Status.FAILED,
    "payment_intent.succeeded": Transaction.Status.SUCCESS,
    "payment_intent.payment_failed": Transaction.Status.FAILED,
}


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhooks(APIView):
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        self.raw_request = None
        super().__init__(**kwargs)

    def account_updated_event(self, event: stripe.Event, stripe_connection: UserStripeConnection):
        if (
            event.data.object.get("details_submitted", False)
            and not stripe_connection.is_onboarding_completed
        ):
            stripe_connection.is_onboarding_completed = True
            stripe_connection.save()
            send_mailing(
                subject="Stripe",
                mail_template="emails/stripe_connected.html",
                users=[stripe_connection.user],
            )

    def session_transaction_events(self, event: stripe.Event):
        transaction_id = event.data.object.get("client_reference_id")
        try:
            transaction = Transaction.objects.get(id=int(transaction_id))
        except (Transaction.DoesNotExist, TypeError):
            request_logger.error("There is no transaction with ID: %s", (transaction_id,))
            return
        transaction.payment_intent = event.data.object.get("payment_intent")
        if not transaction.customer_email:
            if event.data.object.get("customer_email"):
                transaction.customer_email = event.data.object.get("customer_email")
            else:
                transaction.customer_email = event.data.object.get("customer_details", {}).get(
                    "email"
                )
        if event.data.object.get("payment_status") == "paid":
            transaction.status = Transaction.Status.SUCCESS
        if transaction.status != Transaction.Status.SUCCESS:
            transaction.status = SESSION_TRANSACTION_EVENT_TO_STATUS.get(event.get("type"))
        transaction.save()

    def payment_intent_transaction_events(self, event: stripe.Event):
        transaction_payment_intent = event.data.object.get("id")
        try:
            transaction = Transaction.objects.get(payment_intent=transaction_payment_intent)
        except Transaction.DoesNotExist:
            request_logger.error(
                "There is no transaction with payment intent: %s", transaction_payment_intent
            )
            return
        if not transaction.customer_email and event.data.object.get("receipt_email"):
            transaction.customer_email = event.data.object.get("receipt_email")
        if transaction.status != Transaction.Status.SUCCESS:
            transaction.status = PAYMENT_INTENT_TRANSACTION_EVENT_TO_STATUS.get(event.get("type"))
        transaction.save()

    def post(self, request, *args, **kwargs):
        event = stripe.Event.construct_from(request.data, stripe.api_key)
        try:
            stripe_connection = UserStripeConnection.objects.get(
                stripe_account=event.account if hasattr(event, "account") else event.stripe_account
            )
        except UserStripeConnection.DoesNotExist:
            request_logger.error(
                "There is no stripe account with ID: %s",
                (event.account if hasattr(event, "account") else event.stripe_account,),
            )
            # If we return error code, stripe will resend the event
            return Response({"message": "OK"})
        request_logger.info("Incoming Stripe webhook event with type: %s", event.get("type"))
        if event.get("type") == "account.updated":
            self.account_updated_event(event, stripe_connection)

        if event.get("type") in SESSION_TRANSACTION_EVENT_TO_STATUS.keys():
            self.session_transaction_events(event)

        if event.get("type") in PAYMENT_INTENT_TRANSACTION_EVENT_TO_STATUS.keys():
            self.payment_intent_transaction_events(event)

        return Response({"message": "OK"})

    def perform_authentication(self, request):
        sig_header = request.headers.get("stripe-signature")
        try:
            payload = request.body
            if hasattr(payload, "decode"):
                payload = payload.decode("utf-8")
            stripe.WebhookSignature.verify_header(
                payload, sig_header, settings.STRIPE_WEBHOOK_ENDPOINT_SECRET_KEY
            )
        except stripe.error.SignatureVerificationError as e:
            request_logger.critical("Stripe failed to verify webhook secret: %s", e)
            raise AuthenticationFailed("Failed to verify webhook secret")
