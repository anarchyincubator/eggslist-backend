from django.urls import path

from . import views

app_name = "site_configuration"

# fmt: off
urlpatterns = [
    path("location/states", views.LocationStateListAPIView.as_view(), name="location-states"),
    path("location/cities", views.LocationCityListAPIView.as_view(), name="location-cities"),
    path("location/zip-codes", views.LocationZipCodeListAPIView.as_view(), name="location-zip-codes")
]
# fmt: on
