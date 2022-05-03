from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.store import models
from eggslist.store.api import messages, serializers
from eggslist.store.filters import ProductFilter
from eggslist.utils.views.mixins import CacheListAPIMixin


class CategoryListAPIView(CacheListAPIMixin, generics.ListAPIView):
    cache_key = "categories"
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all().prefetch_related("subcategories")


class ProductPagination(PageNumberPagination):
    page_size = 9


class ProductArticleListAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.ProductArticleSerializerSmall
    queryset = models.ProductArticle.objects.get_all_prefetched()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ("title", "description")
    ordering_fields = ("price", "date_created")
    pagination_class = ProductPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ProductArticleSerializer

        return serializers.ProductArticleSerializerSmall

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
