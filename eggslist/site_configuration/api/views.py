from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from eggslist.site_configuration import filters, models
from eggslist.site_configuration.api import serializers
from eggslist.utils.views.mixins import CacheListAPIMixin


class LocationStateListAPIView(CacheListAPIMixin, generics.ListAPIView):
    cache_key = "location_states"
    serializer_class = serializers.StateLocationSerializer
    queryset = models.LocationState.objects.select_related("country").all()


class LocationCityListAPIView(CacheListAPIMixin, generics.ListAPIView):
    cache_key = "location_cities"
    serializer_class = serializers.CityLocationSerializer
    queryset = models.LocationCity.objects.select_related("state__country").all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.LocationCityFilter


class LocationZipCodeListAPIView(generics.ListAPIView):
    serializer_class = serializers.ZipCodeLocationSerializer
    queryset = models.LocationZipCode.objects.select_related("city__state__country").all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.LocationZipCodeFilter
