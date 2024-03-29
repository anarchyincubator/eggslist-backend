from collections import OrderedDict

from django.conf import settings
from django.utils.module_loading import import_string
from django_filters.rest_framework import DjangoFilterBackend
from PIL import Image
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from eggslist.blogs import models
from eggslist.blogs.api import messages, serializers
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


class BlogRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.BlogSerializer
    queryset = models.BlogArticle.objects.select_related(
        "category", "author__zip_code__city__state"
    )
    lookup_field = "slug"
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def permit_operation(self, instance, message: str = messages.ONLY_AUTHOR_CAN_UPDATE):
        if instance.author != self.request.user:
            raise ValidationError({"message": message})

    def perform_update(self, serializer):
        self.permit_operation(serializer.instance)
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        self.permit_operation(instance, message=messages.ONLY_AUTHOR_CAN_DESTROY)
        return super().perform_destroy(instance)


class BlogCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.BlogSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CKEditorImageUpload(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    class NoImageException(Exception):
        pass

    @classmethod
    def image_verify(cls, f):
        try:
            Image.open(f).verify()
        except OSError:
            raise ValidationError({"error": "Image is required"})

    @staticmethod
    def get_storage_class():
        if hasattr(settings, "CKEDITOR_5_FILE_STORAGE"):
            return import_string(settings.CKEDITOR_5_FILE_STORAGE)
        return import_string(settings.DEFAULT_FILE_STORAGE)

    def post(self, request, *args, **kwargs):
        f = request.FILES["upload"]
        self.image_verify(f)
        Storage = self.get_storage_class()
        fs = Storage()
        filename = fs.save(f.name, f)
        url = fs.url(filename)
        return Response({"url": url})
