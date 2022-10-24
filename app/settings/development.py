# flake8: noqa
from .base import *  # noqa

INSTALLED_APPS += ("corsheaders",)
DEBUG = True
SITE_URL = "https://eggslist-frontend.ferialabs.com"
SESSION_COOKIE_DOMAIN = ".ferialabs.com"
