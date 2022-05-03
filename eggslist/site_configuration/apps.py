from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteConfigurationAppsConfig(AppConfig):
    name = "eggslist.site_configuration"
    label = "site_configuration"
    verbose_name = _("site_configuration")
