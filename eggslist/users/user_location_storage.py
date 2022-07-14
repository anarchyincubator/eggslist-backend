import typing as t

from django.core.cache import cache

from eggslist.users.api.constants import USER_LOCATION_COOKIE_AGE

if t.TYPE_CHECKING:
    from eggslist.site_configuration.models import LocationCity


class UserLocationStorage:
    _USER_LOCATION_CACHE_KEY = "user_location_for::user_id::{user_id}"

    @classmethod
    def set_user_location(cls, user_id: str, city_location: "LocationCity"):
        cache.set(
            key=cls._USER_LOCATION_CACHE_KEY.format(user_id=user_id),
            value=city_location,
            timeout=USER_LOCATION_COOKIE_AGE,
        )

    @classmethod
    def get_user_location(cls, user_id: str) -> t.Optional["LocationCity"]:
        return cache.get(key=cls._USER_LOCATION_CACHE_KEY.format(user_id=user_id))
