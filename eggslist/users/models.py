from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    email = models.EmailField(verbose_name=_("email address"), unique=True)
    phone_number = PhoneNumberField(verbose_name=_("phone number"), null=True, blank=True)
    avatar = models.ImageField(verbose_name=_("avatar"), null=True, blank=True)
    is_verified_seller = models.BooleanField(verbose_name=_("is verified seller"), default=False)
    bio = models.CharField(verbose_name=_("bio"), max_length=1024, null=True, blank=True)
    # Location
    zip_code = models.ForeignKey(
        verbose_name=_("zip code"),
        to="site_configuration.LocationZipCode",
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
