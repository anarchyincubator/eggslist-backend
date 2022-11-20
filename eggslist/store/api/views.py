import typing as t

import stripe
from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.store import models
from eggslist.store.api import messages, serializers
from eggslist.store.filters import ProductFilter
from eggslist.utils.views.mixins import AnonymousUserIdAPIMixin
from eggslist.utils.views.pagination import PageNumberPaginationWithCount


class CategoryListAPIView(generics.ListAPIView):
    """Get Product Categories"""

    cache_key = "categories"
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all().prefetch_related("subcategories")


class ProductArticleListAPIView(AnonymousUserIdAPIMixin, generics.ListAPIView):
    """
    Get Product Articles. Use filters as query paramerters.
    Find query parameters information below.
    API method returns the query already filtered according to user location
    if it is provided in Cookie Session
    """

    serializer_class = serializers.ProductArticleSerializerSmall
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = ProductFilter
    search_fields = ("title", "description")
    pagination_class = PageNumberPaginationWithCount

    def get_queryset(self):
        return models.ProductArticle.objects.get_all_catalog_no_hidden(
            user=self.request.user, user_id=self.get_user_id()
        )


class PopularProductListAPIView(AnonymousUserIdAPIMixin, generics.ListAPIView):
    """
    Get Popular products near the user
    """

    serializer_class = serializers.ProductArticleSerializerSmall
    pagination_class = PageNumberPaginationWithCount

    def get_queryset(self):
        return models.ProductArticle.objects.get_all_catalog_no_hidden(
            user=self.request.user, user_id=self.get_user_id()
        )[:8]


class ProfileProductPagination(PageNumberPaginationWithCount):
    page_size = 8


class RecentlyViewedArticleListAPIView(generics.ListAPIView):
    """
    Get recently viewed articles by a current logged user
    """

    serializer_class = serializers.ProductArticleSerializerSmallMy
    pagination_class = ProfileProductPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return models.ProductArticle.objects.get_recently_viewed_for(user=self.request.user)


class MyProductArticlesListAPIView(generics.ListAPIView):
    """
    Get products owned by current user excluding hidden
    """

    serializer_class = serializers.ProductArticleSerializerSmallMy
    pagination_class = ProfileProductPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return models.ProductArticle.objects.get_for(self.request.user)


class MyHiddenProductArticlesListAPIView(generics.ListAPIView):
    """
    Get hidden products owned by a current user
    """

    serializer_class = serializers.ProductArticleSerializerSmallMy
    pagination_class = ProfileProductPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return models.ProductArticle.objects.get_hidden_for(user=self.request.user)


class OtherUserProductArticleListAPIView(generics.ListAPIView):
    """
    Get list of articles belonging to other users
    """

    serializer_class = serializers.ProductArticleSerializerSmall
    pagination_class = ProfileProductPagination
    lookup_field = "seller_id"

    def get_queryset(self):
        return models.ProductArticle.objects.get_for_other(
            user=self.request.user, other_user_id=self.kwargs[self.lookup_field]
        )


class ProductArticleCreateAPIView(AnonymousUserIdAPIMixin, generics.CreateAPIView):
    serializer_class = serializers.ProductArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_serializer_context(self) -> t.Dict:
        context = super().get_serializer_context()

        if hasattr(self.request, "user"):
            context.update(user_id=self.get_user_id())
        return context


class ProductArticleDetailAPIView(AnonymousUserIdAPIMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Return a single product article from all of the locations.
    Return 404 if article is hidden and current user is not an
    owner of the product.
    """

    serializer_class = serializers.ProductArticleSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return models.ProductArticle.objects.get_all_catalog_with_hidden(
            user=self.request.user, user_id=self.get_user_id()
        )

    def get_serializer_context(self) -> t.Dict:
        context = super().get_serializer_context()

        if hasattr(self.request, "user"):
            context.update(user_id=self.get_user_id())
        return context

    def get_object(self):
        instance = super().get_object()
        if instance.seller != self.request.user and instance.is_hidden:
            # Allow only product owner to view it if it's hidden
            raise Http404

        return instance

    def permit_operation(self, instance, message: str = messages.ONLY_SELLER_CAN_UPDATE):
        if instance.seller != self.request.user:
            raise ValidationError({"message": message})

    def perform_destroy(self, instance):
        self.permit_operation(instance)
        return super().perform_destroy(instance)

    def perform_update(self, serializer):
        self.permit_operation(serializer.instance)
        return super().perform_update(serializer)

    def user_viewed(self, product):
        """
        Update `Recently Viewed List`
        """
        user = self.request.user
        if not user.is_authenticated:
            return

        product.user_viewed(user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.user_viewed(product=instance)
        return Response(serializer.data)


class ProductArticleContactButtonAPIView(APIView):
    lookup_field = "slug"

    def post(self, request, *args, **kwargs):
        slug = self.kwargs[self.lookup_field]
        try:
            models.ProductArticle.objects.increase_engagement_count(slug=slug)
        except models.ProductArticle.DoesNotExist:
            raise ValidationError(detail={"message": messages.PRODUCT_ARTICLE_DOES_NOT_EXIST})
        return Response(status=200)


class CreateTransactionAPIView(APIView):
    lookup_field = "slug"
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        product_slug = self.kwargs[self.lookup_field]
        try:
            product = models.ProductArticle.objects.select_related(
                "seller__stripe_connection"
            ).get(slug=product_slug, is_banned=False, is_hidden=False, is_out_of_stock=False)
        except models.ProductArticle.DoesNotExist:
            raise ValidationError(detail={"message": messages.PRODUCT_ARTICLE_DOES_NOT_EXIST})
        stripe_connection = product.seller.stripe_connection
        if not stripe_connection:
            raise ValidationError(
                detail={"message": messages.SELLER_STRIPE_CONNECTION_DOES_NOT_EXIST}
            )

        transaction = models.Transaction.objects.create(
            stripe_connection=stripe_connection,
            product=product,
            price=product.price,
            seller=product.seller,
            customer=request.user,
        )

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
            "stripe_account": stripe_connection.stripe_account,
            "client_reference_id": str(transaction.id),
        }

        if request.user and request.user.email:
            checkout_details["customer_email"] = request.user.email

        session = stripe.checkout.Session.create(**checkout_details)

        return redirect(session.url)


class SellerTransactionsListAPIView(generics.ListAPIView):
    serializer_class = serializers.SellerTransactionListSerializer

    def get_queryset(self):
        return (
            models.Transaction.objects.filter(seller=self.request.user)
            .prefetch_related("product")
            .order_by("-modified_at")
        )


class CustomerTransactionListAPIView(generics.ListAPIView):
    serializer_class = serializers.CustomerTransactionListSerializer

    def get_queryset(self):
        return (
            models.Transaction.objects.filter(customer=self.request.user)
            .prefetch_related("seller")
            .order_by("-modified_at")
        )
