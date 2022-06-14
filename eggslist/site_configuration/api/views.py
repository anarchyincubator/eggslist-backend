from rest_framework import generics

from eggslist.site_configuration import models
from eggslist.site_configuration.api import serializers
from eggslist.utils.views.mixins import CacheListAPIMixin


class LocationCityListAPIView(CacheListAPIMixin, generics.ListAPIView):
    cache_key = "location_cities"
    serializer_class = serializers.CityLocationSerializer
    queryset = models.LocationCity.objects.select_related("state__country").all()
