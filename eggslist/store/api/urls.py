from django.urls import path

from . import views

app_name = "store"

# fmt: off
urlpatterns = [
    path("categories", views.CategoryListAPIView.as_view(), name="categories"),
    path("products", views.ProductArticleListAPIView.as_view(), name="product-list"),
    path("products/popular", views.PopularProductListAPIView.as_view(), name="product-popular"),
    path("products/recently-viewed", views.RecentlyViewedArticleListAPIView.as_view(), name="product-recently-viewed"),
    path("products/my", views.MyProductArticlesListAPIView.as_view(), name="product-my-articles"),
    path("products/other-user/<int:seller_id>", views.OtherUserProductArticleListAPIView.as_view(), name="other-user-product"),
    path("products/my-hidden", views.MyHiddenProductArticlesListAPIView.as_view(), name="product-my-hidden"),
    path("products/create", views.ProductArticleCreateAPIView.as_view(), name="product-create"),
    path("products/<str:slug>", views.ProductArticleDetailAPIView().as_view(), name="product-detail"),
    path("products/<str:slug>/contact", views.ProductArticleContactButtonAPIView.as_view(), name="proudct-contact"),
    path("products/<str:slug>/purchase", views.CreateTransactionAPIView.as_view(), name="product-purchase"),
    path("transactions/customer", views.CustomerTransactionListAPIView.as_view(), name="customer-transactions"),
    path("transactions/seller", views.SellerTransactionsListAPIView.as_view(), name="seller-transactions"),
    path("transactions-recent/seller", views.SellerRecentTransactionListAPIView.as_view(), name="seller-recent-transaction"),
]
# fmt: on
