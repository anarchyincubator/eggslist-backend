from django.apps import apps
from django.contrib.auth.models import UserManager
from django.db import IntegrityError
from django.db.models import Exists, Manager, OuterRef, Value

from eggslist.site_configuration.models import LocationZipCode


class EggslistUserManager(UserManager):
    def _create_user(self, username=None, email=None, password=None, **extra_fields):
        email = self.normalize_email(email)
        if email is None or password is None:
            raise ValueError("`email` and `password` are required fields to create the user")
        if username is None:
            username = email

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        return super().create_user(
            username=username, email=email, password=password, **extra_fields
        )

    def verify_email(self, email: str):
        self.filter(email=email).update(is_email_verified=True)

    def update_location(self, email: str, zip_code_slug: str):
        zip_code = LocationZipCode.objects.get(slug=zip_code_slug)
        self.filter(email=email).update(zip_code=zip_code)

    def get_queryset(self):
        return super().get_queryset().select_related("zip_code__city__state__country")

    def get_for_user(self, user):
        UserFavoriteFarm = apps.get_model("users.UserFavoriteFarm")
        if user.is_authenticated:
            user_favorite_farms = UserFavoriteFarm.objects.filter(
                user=user, following_user=OuterRef("id")
            ).values("following_user")
            return self.annotate(is_favorite=Exists(user_favorite_farms))
        return self.annotate(is_favorite=Value(False))


class UserFavoriteFarmManager(Manager):
    def create_or_delete(self, user_id, following_user_id):
        try:
            self.create(user_id=user_id, following_user_id=following_user_id)
        except IntegrityError:
            self.filter(user_id=user_id, following_user_id=following_user_id).delete()
