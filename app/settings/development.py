# flake8: noqa
from .base import *  # noqa

# INSTALLED_APPS += ("corsheaders",)
DEBUG = True
SITE_URL = "https://eggslist-frontend.ferialabs.com"
SESSION_COOKIE_DOMAIN = ".ferialabs.com"
CSRF_COOKIE_DOMAIN = ".ondigitalocean.app"
CSRF_TRUSTED_ORIGINS = ["https://eggslist-backend-app-qxv36.ondigitalocean.app"]
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "stat_time": {"format": "[%(asctime)s] %(message)s"},
        "verbose": {"format": "{levelname} {asctime} {message}", "style": "{"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "loggers": {
        "django.request": {"handlers": ["mail_admins"], "level": "ERROR", "propagate": True},
        "django.db.backends": {"level": "DEBUG", "handlers": ["console"]},
    },
}
