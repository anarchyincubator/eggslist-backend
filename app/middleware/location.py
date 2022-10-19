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
        response = self.get_response(request)

        if request.COOKIES.get("location_set"):
            return response

        if request.user.is_anonymous:
            user_id = request.COOKIES.get(settings.ANONYMOUS_USER_ID_COOKIE)
        else:
            user_id = request.user.id

        location_city, is_undefined = locate_request(request)
        lookup_radius = settings.DEFAULT_LOOKUP_RADIUS
        UserLocationStorage.set_user_location(
            user_id=user_id,
            city_location=location_city,
            lookup_radius=lookup_radius,
            is_undefined=is_undefined,
        )

        response.set_cookie("location_set", True)
        return response
