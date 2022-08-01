from django.conf import settings
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

from eggslist.utils import constants


class CacheListAPIMixin:
    cache_key = None
    timeout = constants.ONE_HOUR

    def get_queryset(self, *args, **kwargs):
        qs = cache.get(f"view_cache:{self.cache_key}")

        if not qs:
            qs = super().get_queryset(*args, **kwargs)
            cache.set(f"view_cache:{self.cache_key}", qs, timeout=self.timeout)

        return qs


class AnonymousUserIdAPIMixin:
    def get_user_id(self):
        if self.request.user.is_anonymous:
            return self.request.session[settings.ANONYMOUS_USER_ID_SESSION_KEY]
        else:
            return self.request.user.id


class JWTMixin:
    def get_token_data(self, user):
        token = RefreshToken.for_user(user)
        return {"access": str(token.access_token)}
