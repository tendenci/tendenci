import os
import dj_database_url
from . import env

# go one level up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from tendenci.settings import *

SITE_MODE = env('SITE_MODE', 'prod')

ADMINS = ()

MANAGERS = ADMINS

DEBUG = env('DEBUG', False)
TEMPLATE_DEBUG = env('DEBUG', DEBUG)

ROOT_URLCONF = 'conf.urls'

SECRET_KEY = env('SECRET_KEY', 's6324SF3gmt051wtbazonjm4fg0+icbx3rjzcDGFHDR67ua6i')

INSTALLED_APPS += (
    'gunicorn',
)

SITE_ADDONS_PATH = os.path.join(PROJECT_ROOT, 'addons')

# -------------------------------------- #
# DATABASES - ASSUMES HEROKU FOR NOW
# -------------------------------------- #

DATABASES = env('DATABASES', {'default': dj_database_url.config(default='postgres://localhost')})

UNACCENT = env('UNACCENT', False)
if UNACCENT:
    DATABASES['default']['ENGINE'] = 'tendenci.core.base.database'
    SOUTH_DATABASE_ADAPTERS = {'default':'south.db.postgresql_psycopg2'}

# -------------------------------------- #
# DATABASES - EXAMPLE FROM DJANGO 1.4
# -------------------------------------- #
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
"""

# --------------------------------------------- #
# DATABASES - POSTGRES DIRECT CONNECT EXAMPLE
# deploy script will create pg tables, but you need to
# create the db and assign the user/pw first
# --------------------------------------------- #
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tendenci',
        'USER': 'postgresDB',
        'PASSWORD': 'YourSplediferousPasswordForYourDatabaseUserHere',
        'HOST': '127.0.0.1',    # assumes local installation, hence loopback IP
        'PORT': '5432',         # can be blank, or changed. Check docs for your host.
        'OPTIONS': {'autocommit': True},
    }
}
"""

if "postgresql" in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'] = {'autocommit': True}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = env('TIME_ZONE', 'US/Central')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# -------------------------------------- #
# DEBUG OPTIONS
# -------------------------------------- #

if env('SENTRY_DSN', None):
    INSTALLED_APPS += ('raven.contrib.django',)

if env('INTERNAL_IPS', None):
    INTERNAL_IPS = [env('INTERNAL_IPS', '127.0.0.1')]

DEBUG_TOOLBAR = env('DEBUG_TOOLBAR', False)
if DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": True,
    }


# -------------------------------------- #
# THEMES
# -------------------------------------- #

TEMPLATE_DIRS += (os.path.join(PROJECT_ROOT, "themes"),)
THEMES_DIR = os.path.join(PROJECT_ROOT, 'themes')

# ORIGINAL_THEMES_DIR is used when USE_S3_STORAGE==True
ORIGINAL_THEMES_DIR = THEMES_DIR
LOCALE_PATHS += (os.path.join(PROJECT_ROOT, 'themes'),)


# Remote Deploy URL Allows you to pass a URL into the environment
# to trigger a remote action on another server.
# This is used in the theme editor to when a theme file is updated.
#
# The Deploy hooks URL can be used with Heroku deployhooks addon
# https://addons.heroku.com/deployhooks
DEPLOYHOOKS_HTTP_URL = env('DEPLOYHOOKS_HTTP_URL', None)

if DEPLOYHOOKS_HTTP_URL:
    REMOTE_DEPLOY_EXTRA = env('REMOTE_DEPLOY_EXTRA', "theme_edit/")
    REMOTE_DEPLOY_URL = DEPLOYHOOKS_HTTP_URL + REMOTE_DEPLOY_EXTRA

# -------------------------------------- #
# STATIC MEDIA
# -------------------------------------- #

STATICFILES_DIRS += (
    #('media', os.path.join(PROJECT_ROOT, 'site_media/media')),
#    THEMES_DIR,
)

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

# Stock static media files and photos from the URL below
# are licensed by Ed Schipul as Creative Commons Attribution
# http://creativecommons.org/licenses/by/3.0/
#
# The full image set is available online at
# http://tendenci.com/photos/set/3/

STOCK_STATIC_URL = '//d15jim10qtjxjw.cloudfront.net/master-90/'

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.static',
    'tendenci.core.base.context_processors.newrelic',)

# ----------------------------------------- #
# s3 storeage example
# set this up at https://console.aws.amazon.com/console/home
# deploy script will ignore and use local if not configured.
# It's all good.
# ----------------------------------------- #
AWS_LOCATION = env('AWS_LOCATION', '')    # this is usually your site name
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', '')

USE_S3_STORAGE = all([
    AWS_LOCATION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME
])

if USE_S3_STORAGE:

    INSTALLED_APPS += (
        'storages',
        's3_folder_storage',
    )
    # media
    DEFAULT_S3_PATH = "%s/media" % AWS_LOCATION
    DEFAULT_FILE_STORAGE = 'tendenci.libs.boto_s3.utils.DefaultStorage'

    # static
    STATIC_S3_PATH = "%s/static" % AWS_LOCATION
    STATICFILES_STORAGE = 'tendenci.libs.boto_s3.utils.StaticStorage'

    # themes
    THEME_S3_PATH = "%s/themes" % AWS_LOCATION

    S3_ROOT_URL = 'https://s3.amazonaws.com'
    S3_SITE_ROOT_URL = '%s/%s/%s' % (S3_ROOT_URL, AWS_STORAGE_BUCKET_NAME, AWS_LOCATION)

    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = '%s/media/' % S3_SITE_ROOT_URL

    S3_STATIC_ROOT = "/%s/" % STATIC_S3_PATH
    STATIC_URL = '%s/static/' % S3_SITE_ROOT_URL

    # From http://www.tinymce.com/wiki.php/How-to_load_TinyMCE_crossdomain
    # "Please note that it is not possible to load TinyMCE crossdomain"
    # TINYMCE_JS_ROOT = STATIC_ROOT + 'tinymce'
    # TINYMCE_JS_URL = STATIC_URL + 'tinymce/tiny_mce.js'

    S3_THEME_ROOT = "/%s/" % THEME_S3_PATH
    THEMES_DIR = '%s/themes' % S3_SITE_ROOT_URL

    AWS_QUERYSTRING_AUTH = False


# SITE_MODE of dev is used to read the theme locally
# even if S3 settings are setup.
# This setting is 'prod' by default, which will base the theme
# path on whether or not S3 is configured
if SITE_MODE == 'dev':
    USE_S3_THEME = False
else:
    if USE_S3_STORAGE:
        USE_S3_THEME = True


SSL_ENABLED = env('SSL_ENABLED', False)

# celery
CELERY_IS_ACTIVE = env('CELERY_IS_ACTIVE', False)


# -------------------------------------- #
# HAYSTACK SEARCH INDEX
# -------------------------------------- #

HAYSTACK_SEARCH_ENGINE = env('HAYSTACK_SEARCH_ENGINE', 'solr')
HAYSTACK_URL = env('WEBSOLR_URL', 'http://localhost')

if HAYSTACK_SEARCH_ENGINE == "solr":
    HAYSTACK_SOLR_URL = HAYSTACK_URL

if HAYSTACK_SEARCH_ENGINE == 'whoosh':
    HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_ROOT, 'index.whoosh')

INDEX_FILE_CONTENT = env('INDEX_FILE_CONTENT', False)

# ---------------------------------------#
# PAYMENT GATEWAY
# ---------------------------------------#
# authorizenet, firstdata (the first two)
MERCHANT_LOGIN = env('MERCHANT_LOGIN', '')
MERCHANT_TXN_KEY = env('MERCHANT_TXN_KEY', '')
AUTHNET_MD5_HASH_VALUE = env('AUTHNET_MD5_HASH_VALUE', '')
AUTHNET_POST_URL = env('AUTHNET_POST_URL', AUTHNET_POST_URL)

# paypalpayflowlink (currently US only unfortunately per PayPal)
PAYPAL_MERCHANT_LOGIN = env('PAYPAL_MERCHANT_LOGIN', '')
PAYFLOWLINK_PARTNER = env('PAYFLOWLINK_PARTNER', 'PayPal')

# stripe
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', '')

# PayPal
PAYPAL_POST_URL = env('PAYPAL_POST_URL', PAYPAL_POST_URL)

# -------------------------------------- #
# CACHE
# -------------------------------------- #

SITE_CACHE_KEY = env('SECRET_KEY', 'sitename-here')
SITE_SETTINGS_KEY_ENV = env('SITE_SETTINGS_KEY', None)
if SITE_SETTINGS_KEY_ENV:
    SITE_SETTINGS_KEY = SITE_SETTINGS_KEY_ENV

CACHE_PRE_KEY = SITE_CACHE_KEY
JOHNNY_MIDDLEWARE_KEY_PREFIX = SITE_CACHE_KEY
JOHNNY_TABLE_BLACKLIST = ('base_updatetracker')

LOCAL_CACHE_PATH = env('LOCAL_CACHE_PATH', os.path.join(PROJECT_ROOT, "cache"))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Local memcached requires memcached to be running locally.
LOCAL_MEMCACHED_URL = env('LOCAL_MEMCACHED_URL', None)
if LOCAL_MEMCACHED_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': LOCAL_MEMCACHED_URL,
        }
    }

# MEMCACHE
# https://addons.heroku.com/memcache

MEMCACHE_SERVERS = env('MEMCACHE_SERVERS', '')

if MEMCACHE_SERVERS:
    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        }
    }

# MEMCACHIER
# https://addons.heroku.com/memcachier

MEMCACHIER_SERVERS = env('MEMCACHIER_SERVERS', '')

if MEMCACHIER_SERVERS:
    os.environ['MEMCACHE_SERVERS'] = MEMCACHIER_SERVERS
    os.environ['MEMCACHE_USERNAME'] = env('MEMCACHIER_USERNAME', '')
    os.environ['MEMCACHE_PASSWORD'] = env('MEMCACHIER_PASSWORD', '')

    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'LOCATION': MEMCACHIER_SERVERS,
            'BINARY': True,
        }
    }

# Caching defaults

CACHES['default']['TIMEOUT'] = 60 * 60 * 24 * 30  # 30 days
CACHES['default']['JOHNNY_CACHE'] = True


# -------------------------------------- #
# EMAIL NOTIFICATIONS (NOT NEWSLETTERS)
# -------------------------------------- #

EMAIL_USE_TLS = env('EMAIL_USE_TLS', True)
EMAIL_HOST = env('EMAIL_HOST', None)
EMAIL_PORT = env('EMAIL_PORT', None)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', None)

EMAIL_BACKEND = env('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

# SENDGRID

SENDGRID_USERNAME = env('SENDGRID_USERNAME', '')
SENDGRID_PASSWORD = env('SENDGRID_PASSWORD', '')

USE_SENDGRID = all([SENDGRID_USERNAME, SENDGRID_PASSWORD])

if USE_SENDGRID:
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = SENDGRID_USERNAME
    EMAIL_HOST_PASSWORD = SENDGRID_PASSWORD
    EMAIL_PORT = '587'

# MAILGUN

MAILGUN_SMTP_SERVER = env('MAILGUN_SMTP_SERVER', '')
MAILGUN_SMTP_LOGIN = env('MAILGUN_SMTP_LOGIN', '')
MAILGUN_SMTP_PASSWORD = env('MAILGUN_SMTP_PASSWORD', '')
MAILGUN_SMTP_PORT = env('MAILGUN_SMTP_PORT', '')

USE_MAILGUN = all([
    MAILGUN_SMTP_SERVER,
    MAILGUN_SMTP_LOGIN,
    MAILGUN_SMTP_PASSWORD,
    MAILGUN_SMTP_PORT
])

if USE_MAILGUN:
    EMAIL_USE_TLS = True
    EMAIL_HOST = MAILGUN_SMTP_SERVER
    EMAIL_HOST_USER = MAILGUN_SMTP_LOGIN
    EMAIL_HOST_PASSWORD = MAILGUN_SMTP_PASSWORD
    EMAIL_PORT = MAILGUN_SMTP_PORT


DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
SERVER_EMAIL = env('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

try:
    EMAIL_PORT = int(EMAIL_PORT)
except:
    pass

# -------------------------------------- #
# EMAIL NEWSLETTERS USE THIRD PARTY OPTIONS
# -------------------------------------- #

# CAMPAIGN MONITOR
CAMPAIGNMONITOR_URL = env('CAMPAIGNMONITOR_URL', '')
CAMPAIGNMONITOR_API_KEY = env('CAMPAIGNMONITOR_API_KEY', '')
CAMPAIGNMONITOR_API_CLIENT_ID = env('CAMPAIGNMONITOR_API_CLIENT_ID', '')

# -------------------------------------- #
# EMAIL NEWSLETTERS TODO
#   MAIL CHIMP
#   CAMPAIGN MONITOR
#   SALESFORCE
#   BLACKBAUD
#   ETC...
# -------------------------------------- #

# ------------------------------------ #
# IMPERSONATION ADDON
# ------------------------------------ #

if os.path.exists(os.path.join(PROJECT_ROOT, 'addons/impersonation/')):
    MIDDLEWARE_CLASSES += (
        'addons.impersonation.middleware.ImpersonationMiddleware',
    )


# THIS MUST BE AT THE END!
# -------------------------------------- #
# ADDONS
# -------------------------------------- #

DEFAULT_INSTALLED_APPS = INSTALLED_APPS
from tendenci.core.registry.utils import update_addons
INSTALLED_APPS = update_addons(INSTALLED_APPS, SITE_ADDONS_PATH)

# Salesforce Integration
SALESFORCE_USERNAME = env('SALESFORCE_USERNAME', '')
SALESFORCE_PASSWORD = env('SALESFORCE_PASSWORD', '')
SALESFORCE_SECURITY_TOKEN = env('SALESFORCE_SECURITY_TOKEN', '')
SALESFORCE_AUTO_UPDATE = env('SALESFORCE_AUTO_UPDATE', '')
SALESFORCE_SANDBOX = env('SALESFORCE_SANDBOX', False)

MAX_MEMBERSHIP_TYPES = env('MAX_MEMBERSHIP_TYPES', 10)

# local settings for development
try:
    from local_settings import *
except ImportError:
    pass
