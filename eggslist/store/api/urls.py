from django.urls import path

from . import views

app_name = "store"

# fmt: off
urlpatterns = [
    path("categories", views.CategoryListAPIView.as_view(), name="categories"),
    path("products", views.ProductArticleListAPIView.as_view(), name="product-list"),
    path("products/create", views.ProductArticleCreateAPIView.as_view(), name="product-create"),
    path("products/<str:slug>", views.ProductArticleDetailAPIView().as_view(), name="product-detail"),
    path("products/<str:slug>/contact", views.ProductArticleContactButtonAPIView.as_view(), name="proudct-contact")
]
# fmt: on
