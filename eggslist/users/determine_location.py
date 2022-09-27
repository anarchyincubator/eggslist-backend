import typing as t

from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError

from eggslist.site_configuration.models import LocationCity
from eggslist.users.models import UserIPLocationLog


def locate_ip(ip_address: str) -> t.Optional[str]:
    geo_locator = GeoIP2()
    try:
        location = geo_locator.city(ip_address)
    except AddressNotFoundError:
        location = {}
    try:
        UserIPLocationLog.objects.create(
            ip_address=ip_address, determined_city=location.get("city", "")
        )
        user_location = LocationCity.objects.select_related("state__country").get(
            name__iexact=location.get("city", ""), state__name__iexact=location.get("region", "")
        )
    except LocationCity.DoesNotExist:
        return None

    return user_location
