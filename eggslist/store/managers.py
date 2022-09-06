import typing as t

from django.db.models import Exists, F, Manager, OuterRef, Q, QuerySet, Value

from eggslist.users.models import UserFavoriteFarm
from eggslist.users.user_location_storage import UserLocationStorage


class ProductArticlManager(Manager):
    def increase_engagement_count(self, slug: str):
        updted_number = self.filter(slug=slug).update(engagement_count=F("engagement_count") + 1)
        if updted_number == 0:
            raise self.model.DoesNotExist()

    def _get_prefetched(self):
        return self.select_related("seller", "subcategory", "seller__zip_code__city__state")

    def _get_all_prefetched_visible(self, filter_kwargs: t.Optional[t.Dict] = None) -> QuerySet:
        if filter_kwargs is None:
            filter_kwargs = {}
        return self._get_prefetched().filter(is_hidden=False, **filter_kwargs)

    def _get_all_for_city(
        self, city: t.Optional["LocationCity"], filter_kwargs: t.Optional[t.Dict] = None
    ) -> QuerySet:
        """
        Query product for a particular city
        """
        if filter_kwargs is None:
            filter_kwargs = {}

        if city is None:
            return self._get_all_prefetched_visible()

        filter_kwargs.update(seller__zip_code__city=city)
        return self._get_all_prefetched_visible().filter(**filter_kwargs)

    def get_all_prefetched_with_hidden(self) -> QuerySet:
        return self._get_prefetched()

    def get_query_for_user(
        self, user, user_id: t.Union[int, str], filter_kwargs: t.Optional[t.Dict] = None
    ):
        """
        Get QuerySet for a user by user location. If it is an authenticated user annotate favorite farmers.
        """
        city = UserLocationStorage.get_user_location(user_id)
        if user.is_authenticated:
            user_favorite_farms = UserFavoriteFarm.objects.filter(
                user=user, following_user=OuterRef("seller_id")
            ).values("following_user")
            return self._get_all_for_city(city=city, filter_kwargs=filter_kwargs).annotate(
                seller__is_favorite=Exists(user_favorite_farms)
            )

        return self._get_all_for_city(city=city, filter_kwargs=filter_kwargs).annotate(
            seller__is_favorite=Value(False)
        )

    def get_best_similar_for(self, instance) -> QuerySet:
        # TODO: Add favorite farmers annotation
        return (
            self
            # .exclude(slug=instance.slug, is_hidden=True)
            .filter(
                ~Q(slug=instance.slug), ~Q(is_hidden=True), subcategory=instance.subcategory
            ).select_related("seller", "subcategory")[:4]
        )

    def get_from_the_same_farm_for(self, instance) -> QuerySet:
        # TODO: Add favorite farmers annotation
        return self.filter(  # .exclude(slug=instance.slug, is_hidden=True)
            ~Q(slug=instance.slug), ~Q(is_hidden=True), seller=instance.seller
        ).select_related("seller", "subcategory")[:4]

    def get_for(self, user):
        return self._get_all_prefetched_visible(filter_kwargs={"seller": user})

    def get_hidden_for(self, user):
        return self._get_prefetched().filter(seller=user, is_hidden=True)

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

    def get_recently_viewed_for(self, user):
        qs = self.filter(user_view_timestamps__user=user, is_hidden=False)
        return self._annotate_with_favorites(qs, user).order_by(
            "-user_view_timestamps__timestamp"
        )[:8]
