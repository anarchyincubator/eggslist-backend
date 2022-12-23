from django.urls import path

from . import views

app_name = "blogs"

# fmt: off
urlpatterns = [
    path("categories", views.CategoryListAPIView.as_view(), name="blogs-categories"),
    path("blogs", views.BlogListAPIView.as_view(), name="blogs-all"),
    path("blogs/featured", views.FeaturedBlogListAPIView.as_view(), name="blogs-featured"),
    path("blogs/create", views.BlogCreateAPIView.as_view(), name="blogs-create"),
    path("blogs/ckeditor-upload", views.CKEditorImageUpload.as_view(), name="blog-create-ckeditor-upload"),
    path("blogs/<str:slug>", views.BlogRetrieveUpdateDestroyAPIView.as_view(), name="blog-retrieve-update-destroy"),
]
# fmt: on
