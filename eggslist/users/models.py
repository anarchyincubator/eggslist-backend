from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(verbose_name=_("email address"), unique=True)
    avatar = models.ImageField(verbose_name=_("avatar"), null=True, blank=True)
    is_verified_seller = models.BooleanField(verbose_name=_("is verified seller"), default=False)
    bio = models.CharField(verbose_name=_("bio"), max_length=1024, null=True, blank=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
