from django.urls import path

from . import views

app_name = "blogs"

# fmt: off
urlpatterns = [
    path("blogs/featured", views.FeaturedBlogListAPIView.as_view(), name="blogs-featured"),
]
# fmt: on
