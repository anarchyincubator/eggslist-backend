import typing as t

from django.conf import settings
from django.db.models import DecimalField, ExpressionWrapper, Sum, Value
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.store import models
from eggslist.store.api import messages, serializers
from eggslist.store.filters import ProductFilter
from eggslist.users.permissions import IsVerifiedSeller
from eggslist.utils.stripe import api as stripe_api
from eggslist.utils.views.mixins import AnonymousUserIdAPIMixin
from eggslist.utils.views.pagination import PageNumberPaginationWithCount


class CategoryListAPIView(generics.ListAPIView):
    """Get Product Categories"""

    cache_key = "categories"
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all().prefetch_related("subcategories")


class ProductArticleListAPIView(AnonymousUserIdAPIMixin, generics.ListAPIView):
    """
    Get Product Articles. Use filters as query parameters.
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
    Return a single product article from all the locations.
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

    def post(self, request, *args, **kwargs):
        product_slug = self.kwargs[self.lookup_field]
        try:
            product = models.ProductArticle.objects.select_related(
                "seller__stripe_connection"
            ).get(slug=product_slug, is_banned=False, is_hidden=False, is_out_of_stock=False)
        except models.ProductArticle.DoesNotExist:
            raise ValidationError(detail={"message": messages.PRODUCT_ARTICLE_DOES_NOT_EXIST})
        if not hasattr(product.seller, "stripe_connection"):
            raise ValidationError(
                detail={"message": messages.SELLER_STRIPE_CONNECTION_DOES_NOT_EXIST}
            )
        stripe_connection = product.seller.stripe_connection
        if not stripe_connection.is_onboarding_completed:
            raise ValidationError(
                detail={"message": messages.SELLER_NEEDS_STRIPE_ONBOARDING_COMPLETED}
            )
        transaction = models.Transaction.objects.create(
            stripe_connection=stripe_connection,
            product=product,
            price=product.price,
            application_fee=settings.STRIPE_APPLICATION_FEE,
            seller=product.seller,
            customer=request.user if request.user.is_authenticated else None,
        )

        purchase_url = stripe_api.create_purchase_url(
            request.user, stripe_connection, product, transaction.id
        )
        return Response({"redirect_url": purchase_url}, status=200)


class SellerTransactionsListAPIView(generics.GenericAPIView):
    permissions = (IsVerifiedSeller,)
    serializer_class = serializers.SellerTransactionListSerializer
    response_serializer_class = serializers.SellerTransactionListTotalSalesSerializer
    pagination_class = PageNumberPaginationWithCount
    pagination_class.page_size = 20

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return (
            models.Transaction.objects.filter(seller=self.request.user)
            .prefetch_related("product")
            .order_by("-modified_at")
        )

    def get_total_sales_queryset(self):
        return models.Transaction.objects.filter(
            seller=self.request.user, status=models.Transaction.Status.SUCCESS
        ).aggregate(
            total_sales=ExpressionWrapper(
                Sum("price") - (Sum("application_fee") / Value(100.0)),
                output_field=DecimalField(max_digits=8, decimal_places=2),
            )
        )

    def list(self, request, *args, **kwargs):
        list_queryset = self.filter_queryset(self.get_queryset())
        total_sales_queryset = self.get_total_sales_queryset()
        # Default value if seller has no transactions
        if total_sales_queryset.get("total_sales", "") is None:
            total_sales_queryset["total_sales"] = 0

        page = self.paginate_queryset(list_queryset)
        serializer = self.get_serializer(page, many=True)

        list_data = self.paginator.get_paginated_dict(serializer.data)
        return Response(
            self.response_serializer_class(
                total_sales_queryset | {"transaction_list": list_data}
            ).data
        )


class SellerRecentTransactionListAPIView(generics.ListAPIView):
    serializer_class = serializers.SellerTransactionListSerializer
    permission_classes = (IsVerifiedSeller,)

    def get_queryset(self):
        return (
            models.Transaction.objects.filter(seller=self.request.user)
            .prefetch_related("product")
            .order_by("-modified_at")
        )[:3]


class CustomerTransactionListAPIView(generics.ListAPIView):
    serializer_class = serializers.CustomerTransactionListSerializer
    pagination_class = PageNumberPaginationWithCount
    pagination_class.page_size = 20

    def get_queryset(self):
        return (
            models.Transaction.objects.filter(customer=self.request.user)
            .prefetch_related("seller", "product")
            .order_by("-modified_at")
        )
