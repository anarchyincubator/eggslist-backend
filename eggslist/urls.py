from django.urls import include, path

app_name = "eggslist"

urlpatterns = [path("users/", include("eggslist.users.api.urls"))]
