import json
import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "default_config.yaml"), "r") as hr:
    config = yaml.load(hr, Loader=yaml.FullLoader)

for config_key in config:
    if config_key in os.environ:
        if config_key in set(
            [
                "AFTERNOON_ENDS_AT",
                "MORNING_ENDS_AT",
                "POSTGRES_SERVICE_PORT",
                "SLACK_QUERY_MAX_AGE_SECONDS",
            ]
        ):
            config[config_key] = int(os.environ[config_key])
        elif config_key in set(["DJANGO_DEBUG_MODE", "SKIP_NOTIFICATIONS_ON_WE"]):
            config[config_key] = os.environ[config_key].lower() not in (
                "",
                "false",
                "0",
                "f",
            )
        else:
            config[config_key] = os.environ[config_key]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config["DJANGO_SECURITY_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config["DJANGO_DEBUG_MODE"]

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".ngrok.io",
    config["HOSTNAME"],
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    f'https://{config["HOSTNAME"]}',
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "timesheetbot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config["POSTGRES_NAME"],
        "USER": config["POSTGRES_USER"],
        "PASSWORD": config["POSTGRES_PASSWORD"],
        "HOST": config["POSTGRES_SERVICE_HOST"],
        "PORT": config["POSTGRES_SERVICE_PORT"],
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = config["WORKING_TIMEZONE"]
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
