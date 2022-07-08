import typing as t

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from eggslist.site_configuration.models import LocationZipCode
from eggslist.users.user_location_storage import UserLocationStorage

if t.TYPE_CHECKING:
    from eggslist.site_configuration.models import LocationCity


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


class User(AbstractUser):
    email = models.EmailField(verbose_name=_("email address"), unique=True)
    is_email_verified = models.BooleanField(verbose_name=_("is email verified"), default=False)
    phone_number = PhoneNumberField(verbose_name=_("phone number"), null=True, blank=True)
    avatar = models.ImageField(verbose_name=_("avatar"), null=True, blank=True)
    is_verified_seller = models.BooleanField(verbose_name=_("is verified seller"), default=False)
    bio = models.CharField(verbose_name=_("bio"), max_length=1024, null=True, blank=True)
    # Location
    zip_code = models.ForeignKey(
        verbose_name=_("zip code"),
        to="site_configuration.LocationZipCode",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    objects = EggslistUserManager()

    @property
    def user_location(self) -> "LocationCity":
        return UserLocationStorage.get_user_location(self)

    @user_location.setter
    def user_location(self, value: "LocationCity"):
        UserLocationStorage.set_user_location(self, city_location=value)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
