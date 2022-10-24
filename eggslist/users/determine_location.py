import typing as t

from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError

from eggslist.site_configuration.models import LocationCity
from eggslist.users import exceptions
from eggslist.users.models import UserIPLocationLog

if t.TYPE_CHECKING:
    from django.http import HttpRequest


def locate_ip(ip_address: str) -> t.Optional[str]:
    geo_locator = GeoIP2()
    try:
        location = geo_locator.city(ip_address)
    except AddressNotFoundError:
        UserIPLocationLog.objects.create(
            ip_address=ip_address, determined_city="GeoIP2 didn't find it"
        )
        raise exceptions.LocationNotFound
    try:
        user_location = LocationCity.objects.select_related("state__country").get(
            name__iexact=location.get("city", ""), state__name__iexact=location.get("region", "")
        )
    except LocationCity.DoesNotExist:
        UserIPLocationLog.objects.create(
            ip_address=ip_address,
            determined_city=location.get("city", "LocationCity.DoesNotExist"),
        )
        raise exceptions.LocationNotFound

    return user_location


def locate_request(request: "HttpRequest") -> t.Tuple["LocationCity", bool]:
    ip_address = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
    try:
        location_city = locate_ip(ip_address)
        is_undefined = False
    except exceptions.LocationNotFound:
        location_city = LocationCity.objects.get(
            name=settings.DEFAULT_LOCATION["CITY"], state__name=settings.DEFAULT_LOCATION["STATE"]
        )
        is_undefined = True

    return location_city, is_undefined
