import typing as t

from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError

from eggslist.site_configuration.models import LocationCity


def locate_ip(ip_address: str) -> t.Optional[str]:
    geo_locator = GeoIP2()
    try:
        location = geo_locator.city(ip_address)
    except AddressNotFoundError:
        location = {}
    try:
        user_location = LocationCity.objects.get(
            name=location.get("city", ""), state__name=location.get("region", "")
        )
    except LocationCity.DoesNotExist:
        return None

    return user_location
