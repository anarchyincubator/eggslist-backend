from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BlogsAppsConfig(AppConfig):
    name = "eggslist.blogs"
    label = "blogs"
    verbose_name = _("blogs")
