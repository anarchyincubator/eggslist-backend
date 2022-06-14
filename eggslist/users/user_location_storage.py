import typing as t

from django.core.cache import cache

if t.TYPE_CHECKING:
    from eggslist.users.models import User
    from eggslist.site_configuration.models import LocationCity


class UserLocationStorage:
    _USER_LOCATION_CACHE_KEY = "user_location_for::user_id::{user_id}"

    @classmethod
    def set_user_location(cls, user: "User", city_location: "LocationCity"):
        cache.set(key=cls._USER_LOCATION_CACHE_KEY.format(user_id=user.id), value=city_location)

    @classmethod
    def get_user_location(cls, user) -> t.Optional["LocationCity"]:
        return cache.get(key=cls._USER_LOCATION_CACHE_KEY.format(user_id=user.id))
