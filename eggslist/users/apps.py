from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersAppsConfig(AppConfig):
    name = "eggslist.users"
    label = "users"
    verbose_name = _("users")

    def ready(self):
        import eggslist.users.user_create_rule  # noqa
        import eggslist.users.verified_seller_application  # noqa
