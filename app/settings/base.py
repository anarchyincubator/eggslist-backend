from datetime import timedelta

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

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
    "https://eggslist-backend-app-qxv36.ondigitalocean.app",
]
DEFAULT_LOOKUP_RADIUS = 20  # in miles
DEFAULT_LOCATION = {"CITY": "Boston", "STATE": "MA"}

INSTALLED_APPS = (
    # django package
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.sites",
    "app.admin.EggslistAdminConfig",
    "django.contrib.humanize",
    # third-party packages
    "rest_framework",
    "django_filters",
    "solo.apps.SoloAppConfig",
    "phonenumber_field",
    "storages",
    "imagekit",
    "adminsortable2",
    "django_ckeditor_5",
    # project applications
    "eggslist.users",
    "eggslist.site_configuration",
    "eggslist.store",
    "eggslist.blogs",
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "app.middleware.location.LocationMiddleware",
]

ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"

#########################
# Database
#########################

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT", str, ""),
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
DJANGO_SUPERUSER_EMAIL = env("DJANGO_SUPERUSER_EMAIL")
DJANGO_SUPERUSER_PASSWORD = env("DJANGO_SUPERUSER_PASSWORD")
LOCALE_PATHS = (str(APP_DIR.path("app", "locale")),)

# This is for obtaining IP address in instance running in Digital Ocean managed docker application
# Refer to https://www.digitalocean.com/community/questions/client-ip-on-app-platform
IP_ADDRESS_REQUEST_META_KEY = "HTTP_DO_CONNECTING_IP"
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


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
GEOIP_PATH = str(APP_DIR.path("app", "geolite2"))
GEO_ZIP_PATH = f"{GEOIP_PATH}/uszips_states.csv"
GEO_CITIES_PATH = f"{GEOIP_PATH}/us_cities.csv"

#########################
# Rest Framework Settings
#########################

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "app.authentication.CsrfExemptSessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
################
# Authentication
################

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ("eggslist.users.backends.EggslistAuthenticationBackend",)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

USER_LOCATION_COOKIE_NAME = "user_location_id"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_DOMAIN = ".eggslist.com"
CSRF_COOKIE_DOMAIN = ".eggslist.com"
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


######################
# Social Auth Settings
######################
GOOGLE_AUTH_REDIRECT_URL = "social/google/sign-in"
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_SECRET_KEY = env("GOOGLE_SECRET_KEY")
GOOGLE_OAUTH_SCOPE = ["openid", "email", "profile"]
FACEBOOK_AUTH_REDIRECT_URL = "social/facebook/sign-in"
FACEBOOK_CLIENT_ID = env("FACEBOOK_CLIENT_ID")
FACEBOOK_SECRET_KEY = env("FACEBOOK_SECRET_KEY")
FACEBOOK_OAUTH_SCOPE = ["email", "profile"]

######################
# Stripe Settings
######################
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_ENDPOINT_SECRET_KEY = env("STRIPE_WEBHOOK_ENDPOINT_SECRET_KEY")
STRIPE_APPLICATION_FEE = 1
STRIPE_SELLERS_ACCOUNT_TYPE = "standard"
STRIPE_CONNECT_REFRESH_URL = "api/users/connect-stripe"
STRIPE_CONNECT_RETURN_URL = "profile"


######################
# Sentry
######################
sentry_sdk.init(
    dsn=env("SENTRY_URL"),
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True,
    _experiments={
        "profiles_sample_rate": 1.0,
    },
)

###########################
# CKEditor WYSIWYG Settings
###########################
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "link",
            "blockQuote",
            "imageUpload",
        ],
        "heading": {
            "options": [
                {"model": "paragraph", "title": "Paragraph", "class": "ck-heading_paragraph"},
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading5",
                    "view": "h5",
                    "title": "Heading 5",
                    "class": "ck-heading_heading5",
                },
            ]
        },
    }
}
CKEDITOR_5_FILE_STORAGE = "app.storage_backends.CKEditorStorage"
