import django_filters as filters

from eggslist.site_configuration import models


class LocationZipCodeFilter(filters.FilterSet):
    state = filters.CharFilter(
        field_name="city__state__slug",
        help_text="Slug of location state. States could be retrieved by calling `/api/site-configuration/location/states`",
    )
    city = filters.CharFilter(field_name="city__slug", help_text="City slug to be filtered by")

    class Meta:
        model = models.LocationZipCode
        fields = ("state", "city")


class LocationCityFilter(filters.FilterSet):
    state = filters.CharFilter(
        field_name="state__slug",
        help_text="Slug of location state. States could be retrieved by calling `/api/site-configuration/location/states`",
    )

    class Meta:
        model = models.LocationCity
        fields = ("state",)
