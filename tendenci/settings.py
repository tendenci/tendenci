import os.path

# Paths
TENDENCI_ROOT = os.path.abspath(os.path.dirname(__file__))
SITE_ADDONS_PATH = ''

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

"""
For development try FakeSMTP which intercepts SMTP messages for testing
https://github.com/Nilhcem/FakeSMTP

and change these two lines:
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 25

"""

# user agent for external retrieval of files/images
TENDENCI_USER_AGENT = 'Tendenci/5.0 +http://www.tendenci.com'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Central'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', u'English'),
    ('en-us', u'English'),
    ('es', u'Espanol'),
)

LOCALE_PATHS = (
    os.path.join(TENDENCI_ROOT, 'themes'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(TENDENCI_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 's$6*!=msW0__=51^w@_tbaconjm4+fg@0+ic#bx^3rj)zc$a6i'
SITE_SETTINGS_KEY = "FhAiPZWDoxnY0TrakVEFplu2sd3DIli6"

## Django 1.4
TEMPLATE_LOADERS = (
    'tendenci.core.theme.template_loaders.load_template_source',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'tendenci.libs.swfupload.middleware.SWFUploadMiddleware',
    'tendenci.libs.swfupload.middleware.MediaUploadMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tendenci.libs.swfupload.middleware.SSLRedirectMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'tendenci.apps.profiles.middleware.ProfileMiddleware',
    'tendenci.core.base.middleware.Http403Middleware',
    'tendenci.apps.redirects.middleware.RedirectMiddleware',
    'tendenci.core.mobile.middleware.MobileMiddleware',
    'tendenci.core.theme.middleware.RequestMiddleware',
    'tendenci.core.base.middleware.MissingAppMiddleware',
    'tendenci.addons.memberships.middleware.ExceededMaxTypesMiddleware',
)

ROOT_URLCONF = 'tendenci.urls'

# STATIC FILES

USE_S3_STORAGE = False

# Absolute path to the directory that holds static media.
STATIC_ROOT = os.path.join(TENDENCI_ROOT, 'static')

# URL that handles the media served from STATIC_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
LOCAL_STATIC_URL = '/static/'

# Added 2012-03-01 to use cloudfront CDN
STATIC_URL = LOCAL_STATIC_URL

STOCK_STATIC_URL = STATIC_URL

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
)

# other static files besides the STATIC_ROOT
STATICFILES_DIRS = (
)


# AVATARS

# Avatar default URL, no Gravatars
AVATAR_GRAVATAR_BACKUP = False
AVATAR_DEFAULT_URL = STATIC_URL + 'images/icons/default-user-80.jpg'
AUTO_GENERATE_AVATAR_SIZES = (128, 80, 48,)

# default image url (relative to the static folder)
DEFAULT_IMAGE_URL = 'images/default-photo.jpg'

# TEMPLATE DIRECTORIES AND PROCESSORS

TEMPLATE_DIRS = (
    os.path.join(TENDENCI_ROOT, "themes"),
    os.path.join(TENDENCI_ROOT, "templates"),
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',

    # tendenci context processors
    'tendenci.core.theme.context_processors.theme',
    'tendenci.core.site_settings.context_processors.settings',
    'tendenci.core.base.context_processors.static_url',
    'tendenci.core.base.context_processors.index_update_note',
    'tendenci.core.base.context_processors.today',
    'tendenci.core.registry.context_processors.registered_apps',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.formtools',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',

    # applications
    'pagination',
    'tagging',
    'avatar',
    'tinymce',
    'haystack',
    'captcha',
    'south',
    'tastypie',
    'tendenci.libs.model_report',

    'tendenci.apps.entities',
    'tendenci.core.base',
    'tendenci.core.site_settings',
    'tendenci.apps.contributions',
    'tendenci.apps.search',
    'tendenci.apps.notifications',
    'tendenci.apps.registration',
    'tendenci.core.registry',
    'tendenci.core.api_tasty',
    'tendenci.apps.invoices',
    'tendenci.core.payments',
    'tendenci.addons.recurring_payments',
    'tendenci.apps.forms_builder.forms',
    'tendenci.apps.pluginmanager',
    'tendenci.apps.accounts',
    'tendenci.core.files',
    'tendenci.apps.user_groups',
    'tendenci.core.perms',
    'tendenci.apps.dashboard',
    'tendenci.apps.profiles',
    'tendenci.core.meta',
    'tendenci.core.tags',
    'tendenci.addons.articles',
    'tendenci.addons.jobs',
    'tendenci.addons.news',
    'tendenci.apps.stories',
    'tendenci.apps.pages',
    'tendenci.addons.events',
    'tendenci.addons.photos',
    'tendenci.addons.memberships',
    'tendenci.addons.corporate_memberships',
    'tendenci.addons.locations',
    'tendenci.addons.industries',
    'tendenci.addons.regions',
    'tendenci.addons.educations',
    'tendenci.addons.careers',
    'tendenci.core.site_settings',
    'tendenci.addons.make_payments',
    'tendenci.apps.accountings',
    'tendenci.core.emails',
    'tendenci.core.email_blocks',
    'tendenci.apps.subscribers',
    'tendenci.apps.contacts',
    'tendenci.core.robots',
    'tendenci.core.versions',
    'tendenci.core.event_logs',
    'tendenci.core.categories',
    'tendenci.apps.theme_editor',
    'tendenci.libs.styled_forms',
    'tendenci.core.newsletters',
    'tendenci.apps.redirects',
    'tendenci.addons.directories',
    'tendenci.addons.help_files',
    'tendenci.addons.resumes',
    'tendenci.apps.boxes',
    'tendenci.core.mobile',
    'tendenci.addons.social_auth',
    'tendenci.addons.campaign_monitor',
    'tendenci.apps.wp_importer',
    'tendenci.apps.wp_exporter',
    'tendenci.core.theme',
    'tendenci.apps.discounts',
    'tendenci.apps.metrics',
    'tendenci.apps.navs',
    'tendenci.addons.tendenci_guide',
    'tendenci.core.exports',
    'tendenci.addons.events.ics',
    'tendenci.core.imports',
    'tendenci.core.handler404',
    'tendenci.apps.reports',
    # celery task system, must stay at the bottom of installed apps
    'djkombu',
    'djcelery',
)

# This is the number of days users will have to activate their
# accounts after registering. If a user does not activate within
# that period, the account will remain permanently inactive and may
# be deleted by maintenance scripts provided in django-registration.
ACCOUNT_ACTIVATION_DAYS = 7

LOGIN_REDIRECT_URL = '/dashboard'

AUTH_PROFILE_MODULE = 'profiles.Profile'
AUTHENTICATION_BACKENDS = (
    'tendenci.core.perms.backend.ObjectPermBackend',
    'tendenci.addons.social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# -------------------------------------- #
# THEMES
# -------------------------------------- #
THEMES_DIR = os.path.join(TENDENCI_ROOT, 'themes')

# ORIGINAL_THEMES_DIR is used when USE_S3_STORAGE==True
ORIGINAL_THEMES_DIR = THEMES_DIR
USE_S3_THEME = False

# -------------------------------------- #
#    TINYMCE
# -------------------------------------- #
TINYMCE_JS_ROOT = os.path.join(TENDENCI_ROOT, 'static', 'tinymce')
TINYMCE_JS_URL = LOCAL_STATIC_URL + 'tinymce/tiny_mce.js'
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "stormeimage,table,paste,searchreplace,inlinepopups,\
                tabfocus,fullscreen,media,spellchecker,codemirror",
    'gecko_spellcheck': False,
    'theme': "advanced",

    # theme options
    'theme_advanced_buttons1': "bold,italic,underline,strikethrough,|,\
                                bullist,numlist,table, |,justifyleft,\
                                justifycenter,justifyright,|,link,unlink,|,\
                                image,|,pagebreak,fullscreen,codemirror",
    'theme_advanced_buttons2': "formatselect,underline,justifyfull,\
                                forecolor,|,pastetext,pasteword,\
                                removeformat,charmap,|,\
                                outdent,indent,|,undo,redo",
    'theme_advanced_buttons3': "",
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "left",
    'theme_advanced_statusbar_location': "bottom",
    'theme_advanced_resizing': True,


    'theme_advanced_resize_horizontal': True,
    'dialog_type': "modal",
    'tab_focus': ":prev, :next",
    'apply_source_formatting': True,
    'remove_line_breaks': False,
    'convert_urls': False,
    'handle_event_callback': "event_handler",

    # Additions - JMO
    'inline_styles': True,
    'height': 400,
    'extended_valid_elements': "iframe[align<bottom?left?middle?\
                                right?top|class|\
                                frameborder|height|id|longdesc|\
                                marginheight|marginwidth|\
                                name|scrolling<auto?no?yes|src|\
                                style|title|width]"
}

# -------------------------------------- #
# CACHING
# -------------------------------------- #
CACHE_DIR = TENDENCI_ROOT + "/cache"
CACHE_BACKEND = "file://" + CACHE_DIR + "?timeout=604800"   # 7 days
CACHE_PRE_KEY = "TENDENCI"
JOHNNY_MIDDLEWARE_KEY_PREFIX = CACHE_PRE_KEY

# --------------------------------------#
# CELERY
# --------------------------------------#
import djcelery
djcelery.setup_loader()
BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"
CELERY_IS_ACTIVE = False

# USE_SUBPROCESS - in places like exports and long-running
# processes that can timeout, subprocess will be used
# if this setting is True
USE_SUBPROCESS = True

# --------------------------------------#
# Hackstack Search
# --------------------------------------#
HAYSTACK_SITECONF = 'tendenci.apps.search'
HAYSTACK_SEARCH_ENGINE = 'simple'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
HAYSTACK_SOLR_TIMEOUT = 20

# HAYSTACK_INDEX_LIMITS - row amount to index per core application
# Override for rebuild_index command exists in base core app
HAYSTACK_INDEX_LIMITS = {
    'event_logs': 3000,
}

INDEX_FILE_CONTENT = False

# --------------------------------------#
# PAYMENT GATEWAYS
# --------------------------------------#
MERCHANT_LOGIN = ""
MERCHANT_TXN_KEY = ""

# AUTHORIZE.NET
AUTHNET_POST_URL = "https://test.authorize.net/gateway/transact.dll"
AUTHNET_MD5_HASH_VALUE = ''

# FIRSTDATA
FIRSTDATA_POST_URL = 'https://secure.linkpt.net/lpcentral/servlet/lppay'

AUTHNET_CIM_API_TEST_URL = "https://apitest.authorize.net/xml/v1/request.api"
AUTHNET_CIM_API_URL = "https://api.authorize.net/xml/v1/request.api"

# PAYPAL PAYFLOW LINK
PAYFLOWLINK_PARTNER = ''
PAYPAL_MERCHANT_LOGIN = ''
PAYFLOWLINK_POST_URL = 'https://payflowlink.paypal.com'

# PAYPAL
PAYPAL_POST_URL = 'https://www.paypal.com/cgi-bin/webscr'
# for test mode
# PAYPAL_POST_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'

# --------------------------------------#
# RSS
# --------------------------------------#
MAX_RSS_ITEMS = 100
MAX_FEED_ITEMS_PER_APP = 10

# ------------------------------------ #
# Initial Admin Group
# ------------------------------------ #
ADMIN_AUTH_GROUP_NAME = 'Admin'

# --------------------------------------#
# CAPTCHA SETTINGS
# --------------------------------------#
CAPTCHA_FONT_SIZE = 50
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'

# ------------------------------------ #
# Django Messaging
# ------------------------------------ #
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# ------------------------------------ #
# FORMS
# ------------------------------------ #
FORMS_BUILDER_UPLOAD_ROOT = MEDIA_ROOT

# --------------------------------------#
# MOBILE SETTINGS
# --------------------------------------#
MOBILE_COOKIE_NAME = "tendenci_mobile"

# --------------------------------------#
# SWFUPLOAD cookie
# --------------------------------------#
SWFUPLOAD_COOKIE_NAME = 'tendenci_swf'

# ------------------------------------ #
# SOCIAL AUTH SETTINGS
# ------------------------------------ #
LOGIN_ERROR_URL = "/accounts/login_error"
SOCIAL_AUTH_ERROR_KEY = 'social_errors'
SOCIAL_AUTH_COMPLETE_URL_NAME = 'social_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'social_associate_complete'
SOCIAL_AUTH_DEFAULT_USERNAME = 'social_auth_user'
SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True

# ------------------------------------ #
# CAMPAIGN MONITOR URL
# ------------------------------------ #
CAMPAIGNMONITOR_URL = ''

# ------------------------------------ #
# PHOTO SETTINGS
# ------------------------------------ #
PHOTOS_MAXBLOCK = 2 ** 20  # prevents 'IOError: encoder error -2'

# ------------------------------------ #
# MEMBERSHIPS SETTINGS
# ------------------------------------ #
MAX_MEMBERSHIP_TYPES = 10

#-------------------------------------------------------#
# A note for non real time indexes update status
# displaying on the search templates where there non_realtime
# indexes are being used.
#-------------------------------------------------------#
INDEX_UPDATE_NOTE = 'updated hourly'
