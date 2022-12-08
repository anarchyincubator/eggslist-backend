from django.urls import include, path

from eggslist.utils.stripe.views import StripeWebhooks

app_name = "eggslist"

urlpatterns = [
    path("users/", include("eggslist.users.api.urls")),
    path("store/", include("eggslist.store.api.urls")),
    path("blogs/", include("eggslist.blogs.api.urls")),
    path("site-configuration/", include("eggslist.site_configuration.api.urls")),
    path("stripe-webhooks", StripeWebhooks.as_view(), name="stripe-webhook"),
]
