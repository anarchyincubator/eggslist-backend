from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersAppsConfig(AppConfig):
    name = "eggslist.users"
    label = "users"
    verbose_name = _("users")
