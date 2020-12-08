# flake8: noqa
"""
Django settings for paleocore project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
from sys import path
from django.core.exceptions import ImproperlyConfigured

import environ
env = environ.Env()

# Absolute filesystem path to the top-level project folder:

root = environ.Path(__file__) - 3
PROJECT_ROOT = root()
APPS_DIR = root.path('pages')

environ.Env.read_env(root('.env'))

# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = root.path('paleocore')

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# Do not set SECRET_KEY or LDAP password or any other sensitive data here.

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', True)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'compressor',
    'taggit',
    'modelcluster',

    'foundation_formtags',
    'wagtail_feeds',
    'ls.joyous',  # calendar app
    'ckeditor',  # enhanced editing - used by projects app
    'mapwidgets',  # geom editing widgets - used by projects app
    'unicodecsv',  # unicode encoding for csv - used by mlp app
    'import_export',  # generic import-export - used by projects app
    'djgeojson',  # Django geojson
    'leaflet',  # leaflet mapping


    'blog',  # generic blog app
    'contact',  # contact information app
    'documents_gallery',  # documents app
    'gallery',  # image gallery app
    'pages',  # app that contains the site page models
    'people',  # people app
    'products',  # products app
    'publications',  # publications app
    'search',
    'utils',

    # The following apps are interrelated.
    # The individual project apps inherit model classes from the projects app
    'projects',  # projects app
    'standard',  # data standard app
    'drp',  # Dikika Research Project
    'mlp',  # Mille-Logya Project
    'hrp',  # Hadar Research Project
    'lgrp',  # Ledi-Geraru Research Project
    'eppe',  # Eyasi Plateau Paleontology Project
    'gdb',  # Greate Divide Basin
    'omo_mursi',  # Omo Mursi
    'origins',  # Origins
    'psr', # Paleo Silk Road
    'cc',  # Combe Capelle
    'fc',  # Fontechevadpc
    'wtap',  # West Turkana Archaeology Project
    'arvrc',  # African Rift Valley Research Consortium
    'eval',  # Evaluation

    'wagtail.contrib.routable_page',
    'wagtail.contrib.sitemaps',
    'wagtail.contrib.search_promotions',
    'wagtail.contrib.postgres_search',
    'wagtail.contrib.settings',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.modeladmin',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagalytics',
    'wagtailgeowidget',  # geom editing widget - used by projects app
    'allauth',  # universal user authentication app
    'allauth.account',
    'allauth.socialaccount',
    'users',

)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
)


ROOT_URLCONF = 'paleocore.urls'

# Admins see https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""Denne Reed""", 'denne.reed@gmail.com'),
)

MANAGERS = ADMINS

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR.path('templates')), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'paleocore.wsgi.application'


# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

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

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'account_login'

ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapters.SocialAccountAdapter'

ACCOUNT_LOGOUT_REDIRECT_URL = 'account_login'

# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'account_login'


WAGTAILADMIN_RICH_TEXT_EDITORS = {
    'default': {
        'WIDGET': 'wagtail.admin.rich_text.HalloRichTextArea'
    }
}

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///paleocore'),
}

DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = root('static')
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


MEDIA_ROOT = root('media')
MEDIA_URL = '/media/'


# Django compressor settings
# http://django-compressor.readthedocs.org/en/latest/settings/

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

COMPRESS_CACHEABLE_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

COMPRESS_OFFLINE = False


# Settings for wagalytics
# see https://github.com/tomdyson/wagalytics
GA_KEY_FILEPATH = env('GA_KEY_FILEPATH', default='/path/to/secure/directory/your-key.json')
GA_VIEW_ID = env('GA_VIEW_ID', default='ga:xxxxxxxxxxxxx')

# Google Maps Key
try:
    GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')  # don't allow env variables to crash server!
except ImproperlyConfigured:
    GOOGLE_MAPS_API_KEY = ''

# Configuration for  Wagtail Geo Widget
GOOGLE_MAPS_V3_APIKEY = GOOGLE_MAPS_API_KEY

# Configuration for map widgets
DYNAMIC_MAP_URL = ''
STATIC_MAP_URL = ''
MAP_WIDGETS = {
    "GooglePointFieldWidget": (),
    "GOOGLE_MAP_API_KEY": GOOGLE_MAPS_API_KEY,
}


# Wagtail settings

LOGIN_URL = 'wagtailadmin_login'
LOGIN_REDIRECT_URL = 'wagtailadmin_home'

WAGTAIL_SITE_NAME = "paleocore"

# Good for sites having less than a million pages.
# Use Elasticsearch as the search backend for extra performance search results
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.contrib.postgres_search.backend',
    },
}

# Celery settings
# When you have multiple sites using the same Redis server,
# specify a different Redis DB. e.g. redis://localhost/5

BROKER_URL = 'redis://'

CELERY_SEND_TASK_ERROR_EMAILS = True
CELERYD_LOG_COLOR = False
