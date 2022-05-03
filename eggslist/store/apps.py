from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StoreAppsConfig(AppConfig):
    name = "eggslist.store"
    label = "store"
    verbose_name = _("store")

    def ready(self):
        import eggslist.store.article_create_rule  # noqa
