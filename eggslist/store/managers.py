from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos.point import Point
from django.contrib.gis.measure import D
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

    def _annotate_with_distance(self, qs, city) -> QuerySet:
        if city is None:
            # This is to be consistent and always have distance measured.
            # In this case all items will have 0 distance.
            return qs.annotate(distance=Distance(Point(0, 0, srid=4326), Point(0, 0, srid=4326)))
        return qs.annotate(distance=Distance("seller__zip_code__location", city.location))

    def get_recently_viewed_for(self, user):
        qs = self.filter(user_view_timestamps__user=user, is_hidden=False, is_archived=False)
        return self._annotate_with_favorites(qs, user).order_by(
            "-user_view_timestamps__timestamp"
        )[:8]

    def get_for(self, user):
        return self.filter(seller=user, is_hidden=False, is_archived=False).select_related(
            "subcategory",
            "seller__zip_code__city__state",
            "seller__stripe_connection",
        )

    def get_for_other(self, user, other_user_id):
        qs = self.filter(
            seller_id=other_user_id, is_hidden=False, is_archived=False
        ).select_related(
            "subcategory",
            "seller__stripe_connection",
        )
        return self._annotate_with_favorites(qs, user=user)

    def get_hidden_for(self, user):
        return self.filter(seller=user, is_hidden=True, is_archived=False).select_related(
            "subcategory",
            "seller__zip_code__city__state",
            "seller__stripe_connection",
        )

    def get_best_similar_for(self, instance, user, user_id) -> QuerySet:
        city, lookup_radius, is_undefined = UserLocationStorage.get_user_location(user_id=user_id)
        qs = self.select_related(
            "seller__zip_code__city__state", "seller__stripe_connection", "subcategory"
        )
        qs = self._annotate_with_distance(qs, city)
        qs = self._annotate_with_favorites(qs, user=user)
        return qs.filter(
            ~Q(slug=instance.slug),
            subcategory=instance.subcategory,
            is_hidden=False,
            is_archived=False,
            distance__lte=D(mi=lookup_radius),
        )[:4]

    def get_from_the_same_farm_for(self, instance, user, user_id) -> QuerySet:
        city, lookup_radius, is_undefined = UserLocationStorage.get_user_location(user_id=user_id)
        qs = self.select_related(
            "seller__zip_code__city__state", "seller__stripe_connection", "subcategory"
        )
        qs = self._annotate_with_distance(qs, city)
        qs = self._annotate_with_favorites(qs, user=user)
        return qs.filter(
            ~Q(slug=instance.slug), is_hidden=False, is_archived=False, seller=instance.seller
        )[:4]

    def get_all_catalog_no_hidden(self, user, user_id) -> QuerySet:
        city, lookup_radius, is_undefined = UserLocationStorage.get_user_location(user_id=user_id)
        qs = self.select_related(
            "seller__zip_code__city__state", "seller__stripe_connection", "subcategory"
        )
        qs = self._annotate_with_distance(qs, city=city)
        qs = self._annotate_with_favorites(qs, user=user)
        return qs.filter(
            is_hidden=False, is_archived=False, distance__lte=D(mi=int(lookup_radius))
        )

    def get_all_catalog_with_hidden(self, user, user_id):
        qs = self.filter(is_archived=False).select_related(
            "seller__zip_code__city__state", "seller__stripe_connection", "subcategory"
        )
        return self._annotate_with_favorites(qs, user=user)
