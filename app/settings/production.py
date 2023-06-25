from .base import *  # noqa

DEBUG = False
SITE_URL = "https://eggslist.com"
SESSION_COOKIE_DOMAIN = "backend.eggslist.com"
CSRF_TRUSTED_ORIGINS = ["https://backend.eggslist.com", "https://eggslist.com"]
