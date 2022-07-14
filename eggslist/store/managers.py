import typing as t

from django.db.models import F, Manager, QuerySet


class ProductArticlManager(Manager):
    BEST_SIMILAR_CACHE_KEY = "best_similar_for:{subcategory_slug}"

    def increase_engagement_count(self, slug: str):
        updted_number = self.filter(slug=slug).update(engagement_count=F("engagement_count") + 1)
        if updted_number == 0:
            raise self.model.DoesNotExist()

    def get_all_prefetched(self) -> QuerySet:
        return self.all().select_related("seller", "subcategory", "seller__zip_code__city__state")

    def get_all_prefetched_for_city(self, city: t.Optional["LocationCity"]) -> QuerySet:
        if city is None:
            return self.get_all_prefetched()

        return self.get_all_prefetched().filter(seller__zip_code__city=city)

    def get_best_similar_for(self, instance) -> QuerySet:
        qs = (
            self.exclude(slug=instance.slug)
            .filter(subcategory=instance.subcategory)
            .select_related("seller", "subcategory")[:4]
        )
        return qs

    def get_from_the_same_farm_for(self, instance) -> QuerySet:
        return (
            self.exclude(slug=instance.slug)
            .filter(seller=instance.seller)
            .select_related("seller", "subcategory")[:4]
        )
