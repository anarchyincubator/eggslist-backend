from django.urls import path

from . import views

app_name = "store"

# fmt: off
urlpatterns = [
    path("categories", views.CategoryListAPIView.as_view(), name="categories"),
    path("products", views.ProductArticleListAPIView.as_view(), name="product-list"),
    path("products/<str:slug>", views.ProductArticleRetrieveAPIView.as_view(), name="product-retrieve")
]
# fmt: on
