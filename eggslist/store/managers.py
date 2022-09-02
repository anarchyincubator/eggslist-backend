import typing as t

from django.db.models import F, Manager, QuerySet


class ProductArticlManager(Manager):
    def increase_engagement_count(self, slug: str):
        updted_number = self.filter(slug=slug).update(engagement_count=F("engagement_count") + 1)
        if updted_number == 0:
            raise self.model.DoesNotExist()

    def _get_prefetched(self):
        return self.select_related("seller", "subcategory", "seller__zip_code__city__state")

    def get_all_prefetched(self) -> QuerySet:
        return self._get_prefetched().exclude(is_hidden=True)

    def get_all_prefetched_for_city(self, city: t.Optional["LocationCity"]) -> QuerySet:
        if city is None:
            return self.get_all_prefetched()

        return self.get_all_prefetched().filter(seller__zip_code__city=city)

    def get_best_similar_for(self, instance) -> QuerySet:
        return (
            self.exclude(slug=instance.slug)
            .filter(subcategory=instance.subcategory)
            .select_related("seller", "subcategory")[:4]
        )

    def get_from_the_same_farm_for(self, instance) -> QuerySet:
        return (
            self.exclude(slug=instance.slug)
            .filter(seller=instance.seller)
            .select_related("seller", "subcategory")[:4]
        )

    def get_for(self, user):
        return self.get_all_prefetched().filter(seller=user, is_hidden=False)

    def get_hidden_for(self, user):
        return self._get_prefetched().filter(seller=user, is_hidden=True)

    def get_recently_viewed_for(self, user):
        return (
            self.get_all_prefetched()
            .filter(user_view_timestamps__user=user)
            .order_by("-user_view_timestamps__timestamp")[:8]
        )
