import secrets
import typing as t

from django.conf import settings

from eggslist.users.determine_location import locate_request
from eggslist.users.user_location_storage import UserLocationStorage

if t.TYPE_CHECKING:
    from django.http import HttpRequest


class LocationMiddleware:
    def __init__(self, get_response: t.Callable):
        self.get_response = get_response

    def __call__(self, request: "HttpRequest"):
        user_location_id = request.COOKIES.get(settings.USER_LOCATION_COOKIE_NAME, None)

        if user_location_id is None:
            user_location_id = secrets.token_hex(6)

        location_city, lookup_radius, is_undefined = UserLocationStorage.get_user_location(
            user_id=user_location_id
        )

        if location_city is not None:
            return self.get_response(request)

        location_city, is_undefined = locate_request(request)
        lookup_radius = settings.DEFAULT_LOOKUP_RADIUS

        UserLocationStorage.set_user_location(
            user_id=user_location_id,
            city_location=location_city,
            lookup_radius=lookup_radius,
            is_undefined=is_undefined,
        )
        request.COOKIES[settings.USER_LOCATION_COOKIE_NAME] = user_location_id
        response = self.get_response(request)
        response.set_cookie(
            settings.USER_LOCATION_COOKIE_NAME,
            user_location_id,
            domain=settings.SESSION_COOKIE_DOMAIN,
        )
        return response
