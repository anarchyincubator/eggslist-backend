from app.settings import env, APP_DIR

########################
# Environment Variables
########################
DATA_DIR = APP_DIR.path("..", "data")
CONFIG_DIR = APP_DIR.path("..", "conf")

PATHS = {
    "APP_DIR": str(APP_DIR),
    "DATA_DIR": str(DATA_DIR),
    "LOG_DIR": str(APP_DIR.path("..", "logs")),
    "CONFIG_DIR": str(CONFIG_DIR),
    "TMP_DIR": str(APP_DIR.path("..", "tmp")),
    "CACHE_DIR": str(APP_DIR.path("..", "cache")),
    "STATIC_DIR": str(DATA_DIR.path("static", APP_DIR)),
}
SECRET_KEY = env("SECRET_KEY")


#########################
# Application definition
#########################

DEBUG = False
ALLOWED_HOSTS = ["*"]
SITE_ID = 1
SITE_URL = "https://eggslist.com"

INSTALLED_APPS = (
    # django package
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.admin",
    # third-party packages
    "rest_framework",
    "django_filters",
    "solo.apps.SoloAppConfig",
    "phonenumber_field",
    # project applications
    "eggslist.users",
    "eggslist.site_configuration",
    "eggslist.store",
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"

#########################
# Database
#########################

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT", str, ""),
    }
}

#########################
# Cache
#########################

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://:{password}@{host}:{port}/{db}".format(
            password=env("REDIS_PASSWORD"),
            host=env("REDIS_HOST"),
            port=env("REDIS_PORT"),
            db=env("REDIS_DB"),
        ),
        "TIMEOUT": 1200,
    }
}

#########################
# Language
#########################

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_L10N = True
USE_TZ = True

#########################
# Static files
#########################


STATIC_ROOT = PATHS["STATIC_DIR"]
STATIC_URL = "/django-static/"
MEDIA_ROOT = PATHS["DATA_DIR"]

STATICFILES_DIRS = (PATHS["APP_DIR"] + "/app/static/",)
MEDIA_URL = "/data/"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

FILE_UPLOAD_TEMP_DIR = PATHS["TMP_DIR"]
SESSION_FILE_PATH = PATHS["TMP_DIR"]

ADMIN_URL = "admin/"

#########################
# Other settings (Templates, Locale, Context)
#########################

LOCALE_PATHS = (str(APP_DIR.path("app", "locale")),)

AUTH_PASSWORD_VALIDATORS = ()

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APP_DIR.path("app", "templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.csrf",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": False,
        },
    }
]

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

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ("eggslist.users.backends.EggslistAuthenticationBackend",)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": ("app.authentication.CsrfExemptSessionAuthentication",),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

################
# Email sending
################


EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_SSL = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
