from django.core.cache import cache

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
