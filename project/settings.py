import atexit
import os
import sys

from distutils.util import strtobool
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

EASY_RUN_MODE = False  # Variable for fast project start without dealing with environment variables
if EASY_RUN_MODE:
    os.environ['DEBUG'] = 'True'
    os.environ['SECRET_KEY'] = 'VERY_UNIQUE_AND_SECRET_KEY'

IN_TESTING = 'test' in sys.argv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Import environment variables from python file if it exist. For local development only.
if os.path.exists(os.path.join(BASE_DIR, 'project/env_vars.py')):
    """
    Example of file's content:
    import os
    os.environ['DEBUG'] = 'True'
    """
    from project import env_vars  # noqa: F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(strtobool(os.getenv('DEBUG', 'False')))

ALLOWED_HOSTS = [
    'www.ascii-generator.site', '.ascii-generator.site', 'ascii-generator.site',
]

# If DEBUG is True - allow all hosts. For local development only.
if DEBUG:
    ALLOWED_HOSTS.append('*')

# Application definition

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

CUSTOM_APPS = [
    'staff.apps.StaffConfig',
    'app.apps.AppConfig',
]

THIRD_PARTY_APPS = [
    'django_cleanup',
    'captcha',
    'rosetta',
    'django_migration_linter',
]

INSTALLED_APPS = DEFAULT_APPS + CUSTOM_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'staff.middleware.RestrictStaffToAdminMiddleware',  # Restrict staff to admin page
    'django.middleware.locale.LocaleMiddleware',
    'app.middleware.LanguageURLSpecifyMiddleware',  # If language code is in url - set desired language
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

db_postgresql = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USERNAME'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'HOST': os.getenv('DB_HOST', 'localhost'),
    'PORT': os.getenv('DB_PORT', '5432'),
}

db_dummy = {
    'ENGINE': '',
}

DATABASES = {
    'default': db_postgresql,
}

# If EASY_RUN_MODE is True - just don't use any db
if EASY_RUN_MODE:
    DATABASES['default'] = db_dummy

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LOCALE_PATHS = (
    os.path.join(BASE_DIR, '_locale/'),
)

LANGUAGE_CODE = 'en-us'

LANGUAGES_SHORT_CODES = ('en', 'ru',)

LANGUAGES = (
    ('en-us', 'English'),
    ('ru-RU', 'Русский'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# RECAPTCHA API Keys

IGNORE_RECAPTCHA = bool(strtobool(os.getenv('IGNORE_RECAPTCHA', 'False')))
if EASY_RUN_MODE or IN_TESTING or IGNORE_RECAPTCHA:
    RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
    SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
else:
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

# django-rosetta settings

ROSETTA_SHOW_AT_ADMIN_PANEL = True

# temporary images folder

TEMPORARY_IMAGES = os.path.join(BASE_DIR, '_images/temporary/')

if DEBUG:  # If DEBUG is True, at runserver exit delete all the temporary images
    def clear_temporary_images_folder():
        for file_name in os.listdir(TEMPORARY_IMAGES):
            if file_name != '.keep':  # Keep the .keep file
                os.remove(os.path.join(TEMPORARY_IMAGES, file_name))
    atexit.register(clear_temporary_images_folder)

# CACHING

CACHE_TIMEOUT_LONG = 600
CACHE_TIMEOUT_NORMAL = 300

CACHE_LOCMEM = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'unique-snowflake',
    'TIMEOUT': CACHE_TIMEOUT_NORMAL,
}

CACHE_MEMCACHED = {
    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    'LOCATION': '{}:{}'.format(
        os.getenv('MEMCACHED_HOST', '127.0.0.1'),
        os.getenv('MEMCACHED_PORT', '11211'),
    ),
    'TIMEOUT': CACHE_TIMEOUT_NORMAL,
}

CACHES = {
    'default': CACHE_MEMCACHED,
}

if DEBUG or IN_TESTING:
    CACHES['default'] = CACHE_LOCMEM

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', ''),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=False
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
