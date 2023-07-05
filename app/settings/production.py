from .base import *  # noqa

DEBUG = True
SITE_URL = "https://eggslist.com"
SESSION_COOKIE_DOMAIN = "backend.eggslist.com"
CSRF_TRUSTED_ORIGINS = ["https://backend.eggslist.com", "https://eggslist.com"]
