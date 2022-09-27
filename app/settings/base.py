from datetime import timedelta

from app.settings import APP_DIR, env

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
CSRF_TRUSTED_ORIGINS = [
    "https://eggslist.com",
    "https://backend.eggslist.com",
    "http://206.189.255.110",
    "https://206.189.255.110",
    "https://eggslist-dev.ferialabs.com",
]

INSTALLED_APPS = (
    # django package
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # "django.contrib.admin",
    "app.admin.EggslistAdminConfig",
    # third-party packages
    "rest_framework",
    "django_filters",
    "solo.apps.SoloAppConfig",
    "phonenumber_field",
    "storages",
    "imagekit",
    "adminsortable2",
    # project applications
    "eggslist.users",
    "eggslist.site_configuration",
    "eggslist.store",
    "eggslist.blogs",
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "app.middleware.session.AnonymousIdSessionMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "app.middleware.authentication.AnonymousIdAuthenticationMiddleware",
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
# Storage Bucket Settings
AWS_ACCESS_KEY_ID = env("DO_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("DO_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("DO_STORAGE_BUCKET_NAME")
AWS_DEFAULT_ACL = "public-read"
AWS_S3_ENDPOINT_URL = "https://nyc3.digitaloceanspaces.com"
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
# static settings
AWS_LOCATION = "backend-static"
STATIC_URL = "/backend-static/"
STATICFILES_STORAGE = "app.storage_backends.StaticStorage"
# public media settings
PUBLIC_MEDIA_LOCATION = "media"
MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = "app.storage_backends.PublicMediaStorage"


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


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
GEOIP_PATH = str(APP_DIR.path("app", "geolite2"))
GEO_ZIP_PATH = f"{GEOIP_PATH}/uszips_states.csv"

#########################
# Rest Framework Settings
#########################

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "app.authentication.CsrfExemptSessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

################
# Authentication
################

AUTH_USER_MODEL = "users.User"
AUTH_ANONYMOUS_MODEL = "users.AnonymousUser"
AUTHENTICATION_BACKENDS = ("eggslist.users.backends.EggslistAuthenticationBackend",)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ANONYMOUS_USER_ID_SESSION_KEY = "anonymous_id"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365 * 100)  # 100 Years. Just make it unexpierable,
}


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
