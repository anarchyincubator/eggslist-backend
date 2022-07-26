from django.urls import include, path

app_name = "eggslist"

urlpatterns = [
    path("users/", include("eggslist.users.api.urls")),
    path("store/", include("eggslist.store.api.urls")),
    path("blogs/", include("eggslist.blogs.api.urls")),
    path("site-configuration/", include("eggslist.site_configuration.api.urls")),
]
