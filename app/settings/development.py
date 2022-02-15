# flake8: noqa
from .base import *  # noqa

CONFIG = __import__("app.config").config
INSTALLED_APPS += ("corsheaders",)
DEBUG = True
