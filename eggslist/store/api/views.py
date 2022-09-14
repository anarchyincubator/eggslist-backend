import typing as t

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.store import models
from eggslist.store.api import messages, serializers
from eggslist.store.filters import ProductFilter
from eggslist.utils.views.mixins import AnonymousUserIdAPIMixin, CacheListAPIMixin
from eggslist.utils.views.pagination import PageNumberPaginationWithCount


class CategoryListAPIView(CacheListAPIMixin, generics.ListAPIView):
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


class ProductArticleCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.ProductArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductArticleDetailAPIView(AnonymousUserIdAPIMixin, generics.RetrieveUpdateDestroyAPIView):
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
        user = self.request.user
        if not user.is_authenticated:
            return

        product.user_viewed(user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.is_hidden:
            self.permit_operation(instance, message=messages.ONLY_SELLER_CAN_VIEW)

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
