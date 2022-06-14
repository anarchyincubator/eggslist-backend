from django.urls import path

from . import views

app_name = "site_configuration"

# fmt: off
urlpatterns = [
    path("locations", views.LocationCityListAPIView.as_view(), name="ilocations"),
]
# fmt: on
