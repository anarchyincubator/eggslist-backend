from collections import OrderedDict

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from eggslist.blogs import models
from eggslist.blogs.api import serializers
from eggslist.blogs.filters import BlogFilter


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = serializers.CategorySerializer
    queryset = models.BlogCategory.objects.all()


class BlogPagination(PageNumberPagination):
    page_size = 12

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view=view)
        except NotFound:
            return list()

    def get_paginated_response(self, data):
        """Avoid case when self does not have page properties for empty list"""
        if hasattr(self, "page") and self.page is not None:
            return super().get_paginated_response(data)
        else:
            return Response(
                OrderedDict(
                    [("count", None), ("next", None), ("previous", None), ("results", data)]
                )
            )


class FeaturedBlogListAPIView(generics.ListAPIView):
    serializer_class = serializers.BlogSerializerSmall
    queryset = models.BlogArticle.objects.get_featured()
    pagination_class = BlogPagination


class BlogListAPIView(generics.ListAPIView):
    serializer_class = serializers.BlogSerializerSmall
    queryset = models.BlogArticle.objects.select_related("category", "author").order_by("id")
    pagination_class = BlogPagination
    filterset_class = BlogFilter
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("title", "category__name")


class BlogRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.BlogSerializer
    queryset = models.BlogArticle.objects.select_related(
        "category", "author__zip_code__city__state"
    )
    lookup_field = "slug"


class BlogCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.BlogSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
