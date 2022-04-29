from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination

from eggslist.store import models
from eggslist.store.api import serializers
from eggslist.store.api.filters import ProductFilter
from eggslist.utils.views.mixins import CacheListAPIMixin


class CategoryListAPIView(CacheListAPIMixin, generics.ListAPIView):
    cache_key = "categories"
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all().prefetch_related("subcategories")


class ProductArticleListAPIView(generics.ListAPIView):
    serializer_class = serializers.ProductArticleSerializerSmall
    queryset = models.ProductArticle.objects.all().select_related(
        "seller", "subcategory", "seller__zip_code__city__state"
    )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ("title", "description")
    ordering_fields = ("price", "date_created")
    pagination_class = PageNumberPagination


class ProductArticleRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.ProductArticleSerializer
    queryset = models.ProductArticle.objects.all().select_related(
        "seller", "subcategory", "seller__zip_code__city__state"
    )
    lookup_field = "slug"
