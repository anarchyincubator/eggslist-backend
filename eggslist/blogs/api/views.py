from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from eggslist.blogs import models
from eggslist.blogs.api import serializers


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = models.BlogCategory.objects.all()


class BlogPagination(PageNumberPagination):
    page_size = 9


class FeaturedBlogListAPIView(generics.ListAPIView):
    serializer_class = serializers.BlogSerializerSmall
    queryset = models.BlogArticle.objects.get_featured()
    pagination_class = BlogPagination
