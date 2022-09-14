import typing as t

from django.db.models import Exists, F, Manager, OuterRef, Q, QuerySet, Value

from eggslist.users.models import UserFavoriteFarm
from eggslist.users.user_location_storage import UserLocationStorage


class ProductArticlManager(Manager):
    def increase_engagement_count(self, slug: str):
        updted_number = self.filter(slug=slug).update(engagement_count=F("engagement_count") + 1)
        if updted_number == 0:
            raise self.model.DoesNotExist()

    def _annotate_with_favorites(self, qs, user):
        """
        Annotate a queryset with seller__is_favorite parameter. Use only with user.
        If user is not authenticated return Flase in seller__is_favorite
        """
        if not user.is_authenticated:
            return qs.annotate(seller__is_favorite=Value(False))

        user_favorite_farms = Exists(
            UserFavoriteFarm.objects.filter(user=user, following_user=OuterRef("seller_id"))
        )
        return qs.annotate(seller__is_favorite=user_favorite_farms)

    def _get_city_filter_kwargs(self, user_id: t.Union[str, int]) -> t.Dict:
        """
        Get filter kwargs to be included in a `filter` method of a queryset to
        filter it by city
        """
        filter_kwargs = {}
        city = UserLocationStorage.get_user_location(user_id)
        if city is not None:
            filter_kwargs["seller__zip_code__city"] = city

        return filter_kwargs

    def get_recently_viewed_for(self, user):
        qs = self.filter(user_view_timestamps__user=user, is_hidden=False)
        return self._annotate_with_favorites(qs, user).order_by(
            "-user_view_timestamps__timestamp"
        )[:8]

    def get_for(self, user):
        return self.filter(seller=user, is_hidden=False).select_related(
            "subcategory", "seller__zip_code__city__state"
        )

    def get_for_other(self, user, other_user_id):
        qs = self.filter(seller_id=other_user_id, is_hidden=False).select_related(
            "subcategory", "seller"
        )
        return self._annotate_with_favorites(qs, user=user)

    def get_hidden_for(self, user):
        return self.filter(seller=user, is_hidden=True).select_related(
            "subcategory", "seller__zip_code__city__state"
        )

    def get_best_similar_for(self, instance, user, user_id) -> QuerySet:
        city_filter_kwargs = self._get_city_filter_kwargs(user_id=user_id)
        qs = self.filter(
            ~Q(slug=instance.slug),
            ~Q(is_hidden=True),
            subcategory=instance.subcategory,
            **city_filter_kwargs
        ).select_related("seller", "subcategory")
        return self._annotate_with_favorites(qs=qs, user=user)[:4]

    def get_from_the_same_farm_for(self, instance, user, user_id) -> QuerySet:
        city_filter_kwargs = self._get_city_filter_kwargs(user_id=user_id)
        qs = self.filter(
            ~Q(slug=instance.slug),
            ~Q(is_hidden=True),
            seller=instance.seller,
            **city_filter_kwargs
        ).select_related("seller", "subcategory")
        return self._annotate_with_favorites(qs=qs, user=user)[:4]

    def get_all_catalog_no_hidden(self, user, user_id):
        city_filter_kwargs = self._get_city_filter_kwargs(user_id=user_id)
        qs = self.filter(is_hidden=False, **city_filter_kwargs).select_related(
            "seller__zip_code__city", "subcategory"
        )
        return self._annotate_with_favorites(qs, user=user)

    def get_all_catalog_with_hidden(self, user, user_id):
        city_filter_kwargs = self._get_city_filter_kwargs(user_id=user_id)
        qs = self.filter(**city_filter_kwargs).select_related(
            "seller__zip_code__city__state", "subcategory"
        )
        return self._annotate_with_favorites(qs, user=user)
