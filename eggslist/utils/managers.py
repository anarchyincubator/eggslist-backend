from django.core.cache import cache
from django.db import models

from eggslist.utils import constants


class CachedModelManager(models.Manager):
    cache_key = None
    timeout = constants.ONE_HOUR

    def get_queryset(self) -> models.QuerySet:
        qs = cache.get(self.cache_key)
        print("IAM HERE", qs)
        if not qs:
            print("I am getting data from database")
            qs = super().get_queryset()
            cache.set(self.cache_key, qs, timeout=self.timeout)

        return qs

    def create(self, *args, **kwargs) -> models.Model:
        cache.delete(self.cache_key)
        return super().create(*args, **kwargs)
