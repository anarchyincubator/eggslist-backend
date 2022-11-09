"""
Copy this file and rename it to `local.py` and use it as a local 
settings. Include any local settings you want. Here you will find 
required and useful settings.
"""
from .base import *  # noqa
from .development import *  # noqa
import sys

DEBUG = True
TEMPLATES[0]["OPTIONS"]["debug"] = True
SITE_URL = "https://127.0.0.1:8000"
SESSION_COOKIE_DOMAIN = "127.0.0.1"
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

RUN_MODE = sys.argv[1] if len(sys.argv) > 1 else None

LOGGING["loggers"]["django.db.backends"] = {
    "level": "DEBUG",
    "handlers": ["console"],
}

INSTALLED_APPS += ("sslserver",)

if RUN_MODE == "test":

    class DisableMigrations(dict):
        except_apps = {"app_to_run_migrations_for"}

        def __contains__(self, item):
            return item not in self.except_apps

        def __getitem__(self, item):
            return super().__getitem__(item) if item in self.except_apps else None

    MIGRATION_MODULES = DisableMigrations()
