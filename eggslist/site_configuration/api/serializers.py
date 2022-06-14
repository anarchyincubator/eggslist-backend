from rest_framework import serializers

from eggslist.site_configuration import models


class CityLocationSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source="state.name")
    country = serializers.CharField(source="state.country.name")

    class Meta:
        model = models.LocationCity
        fields = ("slug", "name", "state", "country")
