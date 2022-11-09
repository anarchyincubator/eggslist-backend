from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

from eggslist.blogs import models
from eggslist.blogs.api import serializers
from eggslist.blogs.filters import BlogFilter


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = models.BlogCategory.objects.all()


class BlogPagination(PageNumberPagination):
    page_size = 12


class FeaturedBlogListAPIView(generics.ListAPIView):
    serializer_class = serializers.BlogSerializerSmall
    queryset = models.BlogArticle.objects.get_featured()
    pagination_class = BlogPagination


class BlogListAPIView(generics.ListAPIView):
    serializer_class = serializers.BlogSerializerSmall
    queryset = models.BlogArticle.objects.all()
    pagination_class = BlogPagination
    filterset_class = BlogFilter
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("title", "category__name")
