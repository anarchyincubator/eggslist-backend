from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SiteConfigurationAppsConfig(AppConfig):
    name = "eggslist.site_configuration"
    label = "site_configuration"
    verbose_name = _("site_configuration")

    def ready(self):
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
