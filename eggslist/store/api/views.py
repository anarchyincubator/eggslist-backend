from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.store import models
from eggslist.store.api import messages, serializers
from eggslist.store.filters import ProductFilter
from eggslist.users.user_location_storage import UserLocationStorage
from eggslist.utils.views.mixins import AnonymousUserIdAPIMixin, CacheListAPIMixin


class CategoryListAPIView(CacheListAPIMixin, generics.ListAPIView):
    cache_key = "categories"
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all().prefetch_related("subcategories")


class ProductPagination(PageNumberPagination):
    page_size = 9


class ProductArticleListAPIView(AnonymousUserIdAPIMixin, generics.ListAPIView):
    serializer_class = serializers.ProductArticleSerializerSmall
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ("title", "description")
    ordering_fields = ("price", "date_created")
    pagination_class = ProductPagination

    def get_queryset(self):
        location_city = UserLocationStorage.get_user_location(user_id=self.get_user_id())
        return models.ProductArticle.objects.get_all_prefetched_for_city(city=location_city)


class PopularProductListAPIView(AnonymousUserIdAPIMixin, generics.ListAPIView):
    serializer_class = serializers.ProductArticleSerializerSmall
    pagination_class = ProductPagination

    def get_queryset(self):
        location_city = UserLocationStorage.get_user_location(user_id=self.get_user_id())
        return models.ProductArticle.objects.get_all_prefetched_for_city(city=location_city)[:8]


class ProductArticleCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.ProductArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ProductArticleSerializer
    queryset = models.ProductArticle.objects.get_all_prefetched()
    lookup_field = "slug"

    def permit_operation(self, instance):
        if instance.seller != self.request.user:
            raise ValidationError({"message": messages.ONLY_SELLER_CAN_UPDATE})

    def perform_destroy(self, instance):
        self.permit_operation(instance)
        return super().perform_destroy(instance)

    def perform_update(self, serializer):
        self.permit_operation(serializer.instance)
        return super().perform_update(serializer)


class ProductArticleContactButtonAPIView(APIView):
    lookup_field = "slug"

    def post(self, request, *args, **kwargs):
        slug = self.kwargs[self.lookup_field]
        try:
            models.ProductArticle.objects.increase_engagement_count(slug=slug)
        except models.ProductArticle.DoesNotExist:
            raise ValidationError(detail={"message": messages.PRODUCT_ARTICLE_DOES_NOT_EXIST})
        return Response(status=200)
