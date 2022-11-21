from django.urls import path

from . import views

app_name = "blogs"

# fmt: off
urlpatterns = [
    path("categories", views.CategoryListAPIView.as_view(), name="blogs-categories"),
    path("blogs", views.BlogListAPIView.as_view(), name="blogs-all"),
    path("blogs/featured", views.FeaturedBlogListAPIView.as_view(), name="blogs-featured"),
    path("blogs/<str:slug>", views.BlogRetrieveAPIView.as_view(), name="blog-retrieve"),
]
# fmt: on
