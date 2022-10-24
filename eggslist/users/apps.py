from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersAppsConfig(AppConfig):
    name = "eggslist.users"
    label = "users"
    verbose_name = _("users")

    def ready(self):
        import eggslist.users.signals.user_create_rule  # noqa
        import eggslist.users.signals.verified_seller_application  # noqa
        import eggslist.users.signals.change_password_notification  # noqa
