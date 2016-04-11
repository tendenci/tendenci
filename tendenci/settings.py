import os.path

from django.conf import global_settings
import django.conf.locale

# Paths
TENDENCI_ROOT = os.path.abspath(os.path.dirname(__file__))
SITE_ADDONS_PATH = ''

DEBUG = False

ALLOWED_HOSTS = ['*']

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
TENDENCI_USER_AGENT = 'Tendenci/6.0 +https://www.tendenci.com'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Central'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'
# LANGUAGES = (
#     ('en', u'English'),
#     ('es', u'Espanol'),
# )

LOCALE_PATHS = (
    os.path.join(TENDENCI_ROOT, 'locale'),
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

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'tendenci.libs.swfupload.middleware.SWFUploadMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tendenci.libs.swfupload.middleware.SSLRedirectMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'tendenci.apps.profiles.middleware.ForceLogoutProfileMiddleware',
    'tendenci.apps.profiles.middleware.ProfileMiddleware',
    'tendenci.apps.base.middleware.Http403Middleware',
    'tendenci.apps.redirects.middleware.RedirectMiddleware',
    'tendenci.apps.mobile.middleware.MobileMiddleware',
    'tendenci.apps.theme.middleware.RequestMiddleware',
    'tendenci.apps.base.middleware.MissingAppMiddleware',
    'tendenci.apps.memberships.middleware.ExceededMaxTypesMiddleware',
    'tendenci.apps.forums.middleware.PybbMiddleware',
    'tendenci.apps.profiles.middleware.ProfileLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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
AVATAR_DEFAULT_URL = '/images/icons/default-user-80.jpg'
AUTO_GENERATE_AVATAR_SIZES = (128, 80, 48,)

# default image url (relative to the static folder)
DEFAULT_IMAGE_URL = 'images/default-photo.jpg'

# TEMPLATES
TEMPLATES = [
    {
     'BACKEND': 'django.template.backends.django.DjangoTemplates',
#      'APP_DIRS': True,
     'DIRS': [
            os.path.join(TENDENCI_ROOT, "themes"),
            os.path.join(TENDENCI_ROOT, "templates"),
            # Put strings here, like "/home/html/django_templates"
            # or "C:/www/django/templates".
            # Always use forward slashes, even on Windows.
            # Don't forget to use absolute paths, not relative paths.
            ],
     'OPTIONS': {
        'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            
                # tendenci context processors
                'tendenci.apps.theme.context_processors.theme',
                'tendenci.apps.site_settings.context_processors.settings',
                'tendenci.apps.site_settings.context_processors.app_dropdown',
                'tendenci.apps.base.context_processors.static_url',
                'tendenci.apps.base.context_processors.index_update_note',
                'tendenci.apps.base.context_processors.today',
                'tendenci.apps.base.context_processors.site_admin_email',
                'tendenci.apps.base.context_processors.user_classification',
                'tendenci.apps.base.context_processors.display_name',
                'tendenci.apps.registry.context_processors.registered_apps',
                'tendenci.apps.registry.context_processors.enabled_addons',
                'tendenci.apps.forums.context_processors.processor',
                ],
         'loaders':  [
                ('django.template.loaders.cached.Loader', [
                'app_namespace.Loader',
                'tendenci.apps.theme.template_loaders.Loader',
                #'tendenci.apps.theme.template_loaders.load_template_source',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                #'django.template.loaders.eggs.load_template_source',
                ])
            ],
         'debug': DEBUG
        }
     }                
]


INSTALLED_APPS = (
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',

    # applications
    'formtools',
    'bootstrap3',
    'pagination',
    'tagging',
    'avatar',
    'haystack',
    'captcha',
    #'tastypie',
    'tendenci',
    'tendenci.libs.model_report',
    'tendenci.libs.tinymce',

    'tendenci.apps.entities',
    'tendenci.apps.base',
    'tendenci.apps.site_settings',
    'tendenci.apps.contributions',
    'tendenci.apps.search',
    'tendenci.apps.notifications',
    'tendenci.apps.registration',
    'tendenci.apps.registry',
    'tendenci.apps.api_tasty',
    'tendenci.apps.invoices',
    'tendenci.apps.payments',
    'tendenci.apps.recurring_payments',
    'tendenci.apps.forms_builder.forms',
    'tendenci.apps.accounts',
    'tendenci.apps.files',
    'tendenci.apps.user_groups',
    'tendenci.apps.perms',
    'tendenci.apps.profiles',
    'tendenci.apps.meta',
    'tendenci.apps.tags',
    'tendenci.apps.articles',
    'tendenci.apps.jobs',
    'tendenci.apps.news',
    'tendenci.apps.stories',
    'tendenci.apps.pages',
    'tendenci.apps.events',
    'tendenci.apps.photos',
    'tendenci.apps.memberships',
    'tendenci.apps.corporate_memberships',
    'tendenci.apps.locations',
    'tendenci.apps.industries',
    'tendenci.apps.regions',
    'tendenci.apps.educations',
    'tendenci.apps.careers',
    'tendenci.apps.make_payments',
    'tendenci.apps.accountings',
    'tendenci.apps.emails',
    'tendenci.apps.email_blocks',
    #'tendenci.apps.subscribers',
    'tendenci.apps.contacts',
    'tendenci.apps.robots',
    'tendenci.apps.versions',
    'tendenci.apps.event_logs',
    'tendenci.apps.categories',
    'tendenci.apps.theme_editor',
    'tendenci.libs.styled_forms',
    'tendenci.apps.newsletters',
    'tendenci.apps.redirects',
    'tendenci.apps.directories',
    'tendenci.apps.help_files',
    'tendenci.apps.resumes',
    'tendenci.apps.boxes',
    'tendenci.apps.mobile',
    'tendenci.apps.social_auth',
    'tendenci.apps.campaign_monitor',
    'tendenci.apps.wp_importer',
    'tendenci.apps.wp_exporter',
    'tendenci.apps.theme',
    'tendenci.apps.discounts',
    'tendenci.apps.metrics',
    'tendenci.apps.navs',
    'tendenci.apps.tendenci_guide',
    'tendenci.apps.exports',
    'tendenci.apps.events.ics',
    'tendenci.apps.imports',
    'tendenci.apps.handler404',
    'tendenci.apps.reports',
    'tendenci.apps.dashboard',
    'tendenci.apps.social_media',
    'tendenci.apps.announcements',
    'tendenci.apps.forums',
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

AUTHENTICATION_BACKENDS = (
    'tendenci.apps.perms.backend.ObjectPermBackend',
    'tendenci.apps.social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

#--------------------------------------------------
# LANGUAGE
# From: http://stackoverflow.com/questions/12946830/how-to-add-new-languages-into-django-my-language-uyghur-or-uighur-is-not-su
#--------------------------------------------------
EXTRA_LANG_INFO = {
    'tl': {
        'bidi': False, # right-to-left
        'code': 'tl',
        'name': 'Tagalog',
        'name_local': u'Tagalog', #unicode codepoints here
    },
    'tl_PH': {
        'bidi': False, # right-to-left
        'code': 'tl_PH',
        'name': 'Tagalog (Philippines)',
        'name_local': u'Tagalog (Philippines)',
    },
    'he': {
        'bidi': True, # right-to-left
        'code': 'he',
        'name': 'Hebrew',
        'name_local': u'Hebrew', #unicode codepoints here
    },
}

# Add custom languages not provided by Django
LANG_INFO = dict(django.conf.locale.LANG_INFO.items() + EXTRA_LANG_INFO.items())
django.conf.locale.LANG_INFO = LANG_INFO

# Languages using BiDi (right-to-left) layout
LANGUAGES_BIDI = global_settings.LANGUAGES_BIDI + tuple(EXTRA_LANG_INFO.keys())
LANGUAGES = sorted(global_settings.LANGUAGES + tuple([
    (k, v['name']) for k, v in EXTRA_LANG_INFO.items()
    ]), key=lambda x: x[0])

#--------------------------------------------------
# DEBUG TOOLBAR
#--------------------------------------------------
INTERNAL_IPS = ('127.0.0.1', '192.168.0.1', '10.1.0.0', '10.1.4.0',)
DEBUG_TOOLBAR_PATCH_SETTINGS = False

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
#TINYMCE_JS_ROOT = os.path.join(TENDENCI_ROOT, 'static', 'tinymce')
TINYMCE_JS_URL = LOCAL_STATIC_URL + 'tiny_mce/tinymce.min.js'
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False
TINYMCE_FILEBROWSER = True

# plugins: stormeimage codemirror
TINYMCE_DEFAULT_CONFIG = {
    'theme': "modern",
    'plugins': "image  advlist autolink lists link charmap print preview anchor \
        searchreplace visualblocks code fullscreen \
        insertdatetime media table contextmenu paste textcolor colorpicker",
    'menubar': 'file edit insert view format table',
    'toolbar': "code insertfile undo redo | styleselect | forecolor backcolor | bold italic | \
                alignleft aligncenter alignright alignjustify | bullist numlist outdent \
                indent | link image | fullscreen",
    'image_advtab': 'true',
    'media_alt_source': 'false',
    'media_poster': 'false',
    'cache_suffix': '?v=4.3.8',
    # Specify your css to apply to the editable area
    #'content_css': '/themes/<theme name>/media/css/styles.css',
    'resize': 'both',

    'tabfocus_elements': ":prev,:next",
    'convert_urls': 'false',
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
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    }
}

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

# HAYSTACK_INDEX_LIMITS - row amount to index per core application
# Override for rebuild_index command exists in base core app
HAYSTACK_INDEX_LIMITS = {
    'event_logs': 3000,
}

INDEX_FILE_CONTENT = False
HAYSTACK_SIGNAL_PROCESSOR = 'tendenci.apps.search.signals.QueuedSignalProcessor'

# --------------------------------------#
# PAYMENT GATEWAYS
# --------------------------------------#
MERCHANT_LOGIN = ""
MERCHANT_TXN_KEY = ""

# AUTHORIZE.NET
AUTHNET_POST_URL = "https://secure2.authorize.net/gateway/transact.dll"
AUTHNET_MD5_HASH_VALUE = ''

# FIRSTDATA
FIRSTDATA_POST_URL = 'https://secure.linkpt.net/lpcentral/servlet/lppay'

# firstdata e4
FIRSTDATAE4_POST_URL = 'https://checkout.globalgatewaye4.firstdata.com/payment'
#FIRSTDATAE4_POST_URL = 'https://globalgatewaye4.firstdata.com/pay'
FIRSTDATA_RESPONSE_KEY = ''
FIRSTDATA_USE_RELAY_RESPONSE = False

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

# ----------------------------------- #
# Django Admin Bootstrap
# ------------------------------------#
DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

from django.contrib import messages

MESSAGE_TAGS = {
            messages.SUCCESS: 'alert-success success',
            messages.WARNING: 'alert-warning warning',
            messages.ERROR: 'alert-danger error'
}

# -------------------------------------- #
# EMAIL Settings for Newsletters
# -------------------------------------- #
NEWSLETTER_EMAIL_HOST = None
NEWSLETTER_EMAIL_PORT = 587     # 587 is the default for mailgun
NEWSLETTER_EMAIL_HOST_USER = ''
NEWSLETTER_EMAIL_HOST_PASSWORD = ''
NEWSLETTER_EMAIL_USE_TLS = True
NEWSLETTER_EMAIL_BACKEND = 'tendenci.apps.emails.backends.NewsletterEmailBackend'

# -------------------------------------- #
# pybb forum
# -------------------------------------- #
PYBB_MARKUP = 'markdown'
PYBB_NICE_URL = True
PYBB_ATTACHMENT_ENABLE = True
