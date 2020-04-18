import os.path
from django import __path__ as django_path


# ---------------------------------------------------------------------------- #
# Paths
# ---------------------------------------------------------------------------- #

AWS_LOCATION = ''
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
USE_S3_STORAGE = False
THEME_S3_PATH = 'themes'
USE_S3_THEME = False

TENDENCI_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.environ['TENDENCI_PROJECT_ROOT']

LOCALE_PATHS = [os.path.join(TENDENCI_ROOT, 'locale')]

SITE_ADDONS_PATH = os.path.join(PROJECT_ROOT, 'addons')

BUILTIN_THEMES_DIR = os.path.join(TENDENCI_ROOT, 'themes')

THEMES_DIR = os.path.join(PROJECT_ROOT, 'themes')
# ORIGINAL_THEMES_DIR is used when USE_S3_STORAGE==True
ORIGINAL_THEMES_DIR = THEMES_DIR

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
# Path for photos relative to MEDIA_ROOT and MEDIA_URL
PHOTOS_DIR = 'photos'
FORMS_BUILDER_UPLOAD_ROOT = MEDIA_ROOT

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
# URL that handles the media served from STATIC_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
LOCAL_STATIC_URL = '/static/'
STATIC_URL = LOCAL_STATIC_URL  # Added 2012-03-01 to use cloudfront CDN
# Stock static media files and photos from the URL below
# are licensed by Ed Schipul as Creative Commons Attribution
# http://creativecommons.org/licenses/by/3.0/
#
# The full image set is available online at
# http://tendenci.com/photos/set/3/
STOCK_STATIC_URL = '//d15jim10qtjxjw.cloudfront.net/master-90/'


# ---------------------------------------------------------------------------- #
# Django
# ---------------------------------------------------------------------------- #

DEBUG = False

SITE_ID = 1

ROOT_URLCONF = 'tendenci.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'localhost',
        'PORT': 5432,
        'USER': 'tendenci',
        'PASSWORD': 'tendenci',
        'NAME': 'tendenci',
    }
}

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'dj_pagination.middleware.PaginationMiddleware',
    'tendenci.apps.profiles.middleware.ForceLogoutProfileMiddleware',
    'tendenci.apps.profiles.middleware.ProfileMiddleware',
    'tendenci.apps.base.middleware.Http403Middleware',
    'tendenci.apps.redirects.middleware.RedirectMiddleware',
    'tendenci.apps.mobile.middleware.MobileMiddleware',
    'tendenci.apps.theme.middleware.RequestMiddleware',
    'tendenci.apps.base.middleware.MissingAppMiddleware',
    'tendenci.apps.base.middleware.RemoveNullByteMiddleware',
    'tendenci.apps.memberships.middleware.ExceededMaxTypesMiddleware',
    'tendenci.apps.forums.middleware.PybbMiddleware',
    'tendenci.apps.profiles.middleware.ProfileLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]
if os.path.exists(os.path.join(PROJECT_ROOT, 'addons/impersonation/')):
    MIDDLEWARE += ['addons.impersonation.middleware.ImpersonationMiddleware']

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {
      'context_processors': [
        'django.contrib.auth.context_processors.auth',
        'django.template.context_processors.debug',
        'django.template.context_processors.i18n',
        'django.template.context_processors.media',
        'django.template.context_processors.request',
        'django.template.context_processors.static',
        'django.contrib.messages.context_processors.messages',
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
        'tendenci.apps.base.context_processors.newrelic',
      ],
      'loaders': [
        ('tendenci.apps.theme.template_loaders.CachedLoader', [
          'app_namespace.Loader',
          'tendenci.apps.theme.template_loaders.ThemeLoader',
          'django.template.loaders.filesystem.Loader',
          'django.template.loaders.app_directories.Loader',
        ])
      ],
      'libraries': {
        # tendenci.apps.theme.templatetags.static replaces these, so rename them
        # to avoid conflicts
        'django.static': 'django.contrib.staticfiles.templatetags.staticfiles',
        'django.staticfiles': 'django.templatetags.static',
      },
      'builtins': [
        'tendenci.apps.theme.templatetags.static',
        'django.templatetags.i18n',
      ],
    },
    'DIRS': [django_path[0]+'/forms/templates'],
  }
]
def disable_template_cache():  # For use in site-specific settings.py
    TEMPLATES[0]['OPTIONS']['loaders'] = TEMPLATES[0]['OPTIONS']['loaders'][0][1]
# The form renderer does not use the TEMPLATES setting by default.  Configure it to use the
# TEMPLATES setting so that form widget templates can be overridden in themes.
# This requires either adding 'django.forms' to INSTALLED_APPS or adding
# django_path[0]+'/forms/templates' to TEMPLATES['DIRS'].  Since adding 'django.forms' to
# INSTALLED_APPS creates an app name conflict with 'tendenci.apps.forms_builder.forms', we must
# use TEMPLATES['DIRS'] instead.
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

INSTALLED_APPS = [
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
    'django.contrib.gis',

    'formtools',
    'bootstrap3',
    'dj_pagination',
    'tagging',
    'captcha',
    'haystack',
    'tastypie',
    'timezone_field',
    'gunicorn',

    'tendenci.libs.model_report',
    'tendenci.libs.tinymce',
    'tendenci.libs.uploader',

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
    'tendenci.apps.payments.stripe',
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
    #'tendenci.apps.social_auth',  # Does not support Python 3
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
    'tendenci.apps.committees',
    'tendenci.apps.case_studies',
    'tendenci.apps.donations',
    'tendenci.apps.speakers',
    'tendenci.apps.staff',
    'tendenci.apps.studygroups',
    'tendenci.apps.videos',
    'tendenci.apps.testimonials',
    'tendenci.apps.social_services',

    # Django SQL Explorer
    'tendenci.apps.explorer_extensions',
    'explorer',

#     # Celery Task System, must stay at the bottom of installed apps
#     'kombu.transport.django',
#     'djcelery',
]

LOGIN_REDIRECT_URL = '/dashboard'
AUTHENTICATION_BACKENDS = [
    'tendenci.apps.perms.backend.ObjectPermBackend',
    #'tendenci.apps.social_auth.backends.facebook.FacebookBackend',  # Does not support Python 3
    'django.contrib.auth.backends.ModelBackend',
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
DEFAULT_FROM_EMAIL = 'root@localhost'

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
]
# Additional paths to collect static files from when populating STATIC_ROOT
STATICFILES_DIRS = []
# Collect static files from builtin themes
for theme in os.listdir(BUILTIN_THEMES_DIR):
    # Ignore '.' '..' and hidden directories
    if theme.startswith('.'):
        continue
    theme_path = os.path.join(BUILTIN_THEMES_DIR, theme)
    if not os.path.isdir(theme_path):
        continue
    for static_dir in ['media', 'static']:
        static_path = os.path.join(theme_path, static_dir)
        if os.path.isdir(static_path):
            prefix = os.path.join('themes', theme)
            STATICFILES_DIRS += [(prefix, static_path)]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 60*60*24*30,  # 30 days
    }
}
try:
    import pylibmc
except ImportError:
    CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'root': {
        # Set the default logger level to DEBUG so that all messages are passed
        # to the handlers and the handlers can decide which messages to actually
        # log.
        'level': 'DEBUG',
        'handlers': ['file', 'debug_file', 'mail_admins'],
    },
    'loggers': {
        # The 'django' logger must be defined to override the defaults
        # configured by Django:
        # https://github.com/django/django/blob/master/django/utils/log.py
        'django': {
            'level': 'DEBUG',
            # Disable the default handlers
            'handlers': [],
            # And use the 'root' handlers above instead
            'propagate': True,
        },
        # django.db.backends logs all SQL statements at DEBUG level when
        # settings.DEBUG is True.  That produces lots of log messages, so set
        # the level at INFO to filter them.
        'django.db.backends': {
            'level': 'INFO',
        },
        # The Daphne web server logs connection details at DEBUG level.  That
        # produces lots of log messages, so set the level at INFO to filter
        # them when running under Daphne.
        # In addition, Daphne logs ERRORs when workers are stopped/started.  It
        # is probably unnecessary to send emails for those, so disable the
        # mail_admins handler for Daphne logs.
        'daphne': {
            'level': 'INFO',
            'handlers': ['file', 'debug_file'],
            'propagate': False,
        },
        # Python Warnings are primarily used for deprecation warning messages.
        # Enable them only when DEBUG is True.
        'py.warnings': {
            'filters': ['require_debug_true'],
        },
    },
    'formatters': {
        'info': {
            'format': 'TIME="%(asctime)s" LEVEL=%(levelname)s PID=%(process)d LOGGER="%(name)s" MSG="%(message)s"'
        },
        'debug': {
            'format': 'TIME="%(asctime)s" LEVEL=%(levelname)s PID=%(process)d LOGGER="%(name)s" FILE="%(pathname)s" LINE=%(lineno)s FUNC="%(funcName)s" MSG="%(message)s"'
        },
    },
    'handlers': {
        # FileHandler is thread safe but not multi-process safe, so log output could be interleaved
        # if multiple worker processes generate a log message at the same time.  Since Django and
        # Tendenci logging is minimal and mostly non-critical, this is not likely to be much of a
        # problem in most cases.  However, if you need multi-process safe logging, use SysLogHandler
        # or SocketHandler with a log server such as https://pypi.python.org/pypi/multilog .
        #
        # DO NOT use RotatingFileHandler or TimedRotatingFileHandler here, as their rotation
        # behavior is not multi-process safe and will cause data to be lost from rotated log files.
        # When using those Handlers, each process will redundantly rotate the files and will
        # overwrite any files previously rotated by another process.  If you need logs to be
        # automatically rotated, either use logrotate (and restart Tendenci after rotation), or use
        # SocketHandler with a log server such as multilog which can then safely use
        # RotatingFileHandler or TimedRotatingFileHandler.
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.FileHandler',
            'filename': '/var/log/tendenci/app.log',
        },
        'debug_file': {
            'filters': ['require_debug_true'],
            'level': 'DEBUG',
            'formatter': 'debug',
            'class': 'logging.FileHandler',
            'filename': '/var/log/tendenci/debug.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'tendenci.apps.base.log.CustomAdminEmailHandler',
        },
        'discard': {
            'level': 'CRITICAL',
            'class': 'logging.NullHandler',
        },
    },
}
# For use in site-specific settings.py
def set_app_log_filename(filename):
    LOGGING['handlers']['file']['filename'] = filename
def set_debug_log_filename(filename):
    LOGGING['handlers']['debug_file']['filename'] = filename
def set_app_log_level(level):
    LOGGING['handlers']['file']['level'] = level
def set_console_log_level(level):
    LOGGING['handlers']['console']['level'] = level
def disable_app_log():
    LOGGING['root']['handlers'].remove('file')
def disable_debug_log():
    LOGGING['root']['handlers'].remove('debug_file')
def disable_admin_emails():
    LOGGING['root']['handlers'].remove('mail_admins')
def enable_console_log():
    LOGGING['root']['handlers'] = ['console'] + LOGGING['root']['handlers']

# By default, Python Warnings are logged directly to the console.  The following
# lines redirect them to the logger.
import logging  # noqa: E402
logging.captureWarnings(True)
# To disable redirection to the logger:
#logging.captureWarnings(False)

# By default, most Python Warnings are disabled.  The following lines enable
# them unless python was run with the -W option to override this behavior.
import sys  # noqa: E402
if not sys.warnoptions:
    import warnings  # noqa: E402
    warnings.simplefilter("default")
# To restore Python's default Warnings filters:
#warnings.resetwarnings()


# ---------------------------------------------------------------------------- #
# Languages
# ---------------------------------------------------------------------------- #

# From: http://stackoverflow.com/questions/12946830/how-to-add-new-languages-into-django-my-language-uyghur-or-uighur-is-not-su

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
import django.conf.locale  # noqa: E402
LANG_INFO = dict(list(django.conf.locale.LANG_INFO.items()) + list(EXTRA_LANG_INFO.items()))
django.conf.locale.LANG_INFO = LANG_INFO

# Languages using BiDi (right-to-left) layout
from django.conf import global_settings  # noqa: E402
LANGUAGES_BIDI = global_settings.LANGUAGES_BIDI + list(EXTRA_LANG_INFO.keys())
LANGUAGES = sorted(global_settings.LANGUAGES + [
    (k, v['name']) for k, v in EXTRA_LANG_INFO.items()
    ], key=lambda x: x[0])


# ---------------------------------------------------------------------------- #
# Tendenci
# ---------------------------------------------------------------------------- #

SSL_ENABLED = False

SITE_CACHE_KEY = 'tendenci'
CACHE_PRE_KEY = SITE_CACHE_KEY


# This is the number of days users will have to activate their
# accounts after registering. If a user does not activate within
# that period, the account will remain permanently inactive and may
# be deleted by maintenance scripts provided in django-registration.
ACCOUNT_ACTIVATION_DAYS = 7

MAX_MEMBERSHIP_TYPES = 10

MAX_RSS_ITEMS = 100
MAX_FEED_ITEMS_PER_APP = 10

# A note for non real time indexes update status displaying on the search
# templates where non real time indexes are being used.
INDEX_UPDATE_NOTE = 'updated hourly'

GAVATAR_DEFAULT_SIZE = 80
GAVATAR_DEFAULT_URL = 'images/icons/default-user-80.jpg'

# Default image url (relative to the static folder)
DEFAULT_IMAGE_URL = 'images/default-photo.jpg'

# User agent for external retrieval of files/images
TENDENCI_USER_AGENT = 'Tendenci/11 (+https://www.tendenci.com)'

# Google Static Maps URL signing secret used to generate a digital signature
GOOGLE_SMAPS_URL_SIGNING_SECRET = ''

# Files App
ALLOW_MP3_UPLOAD = False

# Photos App
PHOTOS_MAXBLOCK = 2 ** 20  # prevents 'IOError: encoder error -2'

# Events
# Turn on/off the Gratuity feature - per Ed, allow it to be adjusted in conf/settings.py rather than site settings
EVENTS_GRATUITY_ENABLED = False

# EMail Settings for Newsletters
NEWSLETTER_EMAIL_HOST = None
NEWSLETTER_EMAIL_PORT = 587     # 587 is the default for mailgun
NEWSLETTER_EMAIL_HOST_USER = ''
NEWSLETTER_EMAIL_HOST_PASSWORD = ''
NEWSLETTER_EMAIL_USE_TLS = True
NEWSLETTER_EMAIL_BACKEND = 'tendenci.apps.emails.backends.NewsletterEmailBackend'

# Mobile App
MOBILE_COOKIE_NAME = "tendenci_mobile"

# Forums App
PYBB_MARKUP = 'markdown'
PYBB_NICE_URL = True
PYBB_ATTACHMENT_ENABLE = True

# HelpDesk App
HELPDESK_REDIRECT_TO_LOGIN_BY_DEFAULT = False

# Campaign Monitor App
CAMPAIGNMONITOR_URL = ''
CAMPAIGNMONITOR_API_KEY = ''
CAMPAIGNMONITOR_API_CLIENT_ID = ''

# Social Auth App
LOGIN_ERROR_URL = "/accounts/login_error"
SOCIAL_AUTH_ERROR_KEY = 'social_errors'
SOCIAL_AUTH_COMPLETE_URL_NAME = 'social_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'social_associate_complete'
SOCIAL_AUTH_DEFAULT_USERNAME = 'social_auth_user'
SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True

# if True, show alert for tendenci update (if needed) for superuser on login
SHOW_UPDATE_ALERT = False


# ---------------------------------------------------------------------------- #
# TinyMCE Editor
# ---------------------------------------------------------------------------- #

#TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, 'tinymce')
TINYMCE_JS_URL = 'tiny_mce/tinymce.min.js'
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False
TINYMCE_FILEBROWSER = True

# plugins: stormeimage codemirror
TINYMCE_DEFAULT_CONFIG = {
    'theme': "modern",
    'plugins': "image  advlist autolink lists link charmap print preview anchor \
        searchreplace visualblocks code fullscreen \
        insertdatetime media table contextmenu paste textcolor colorpicker hr",
    'menubar': 'file edit insert view format table',
    'toolbar': "code insertfile undo redo | styleselect | forecolor backcolor | bold italic hr | \
                alignleft aligncenter alignright alignjustify | bullist numlist outdent \
                indent | link image | fullscreen",
    'image_advtab': 'true',
    'image_title': 'true',
    'media_alt_source': 'false',
    'media_poster': 'false',
    'cache_suffix': '?v=4.3.8',
    # Specify your css to apply to the editable area
    #'content_css': '/static/themes/<theme name>/css/styles.css',
    'resize': 'both',
    'link_class_list': [
        {'title': 'None', 'value': ''},
        {'title': 'Primary Button', 'value': 'btn btn-primary'},
        {'title': 'Default Button', 'value': 'btn btn-default'}
        ],
    'image_class_list': [
        {'title': 'none', 'value': ''},
        {'title': 'img-responsive', 'value': 'img-responsive'},
       ],
    'tabfocus_elements': ":prev,:next",
    'convert_urls': 'false',
    'handle_event_callback': "event_handler",

    # Additions - JMO
    'inline_styles': True,
    'height': 400,
    'extended_valid_elements': "iframe[align<bottom?left?middle?\
                                right?top|class|allowfullscreen|\
                                frameborder|height|id|longdesc|\
                                marginheight|marginwidth|\
                                name|scrolling<auto?no?yes|src|\
                                style|title|width|html|head|title|meta|body|style]"
}


# ---------------------------------------------------------------------------- #
# Payment Gateways
# ---------------------------------------------------------------------------- #

MERCHANT_LOGIN = ''
MERCHANT_TXN_KEY = ''

# Authorize.Net
AUTHNET_POST_URL = 'https://secure2.authorize.net/gateway/transact.dll'
AUTHNET_SIGNATURE_KEY = ''

AUTHNET_CIM_API_TEST_URL = 'https://apitest.authorize.net/xml/v1/request.api'
AUTHNET_CIM_API_URL = 'https://api2.authorize.net/xml/v1/request.api'

# FirstData
FIRSTDATA_POST_URL = 'https://secure.linkpt.net/lpcentral/servlet/lppay'

# FirstData E4
FIRSTDATAE4_POST_URL = 'https://checkout.globalgatewaye4.firstdata.com/payment'
#FIRSTDATAE4_POST_URL = 'https://globalgatewaye4.firstdata.com/pay'
FIRSTDATA_RESPONSE_KEY = ''
FIRSTDATA_USE_RELAY_RESPONSE = False

# PayPal PayFlow Link
PAYFLOWLINK_PARTNER = ''
PAYPAL_MERCHANT_LOGIN = ''
PAYFLOWLINK_POST_URL = 'https://payflowlink.paypal.com'

# PayPal
PAYPAL_POST_URL = 'https://www.paypal.com/cgi-bin/webscr'
PAYPAL_SANDBOX_POST_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'

# Stripe
STRIPE_SECRET_KEY = ''
STRIPE_PUBLISHABLE_KEY = ''
STRIPE_API_VERSION = '2019-08-14'

# List of merchant accounts you can set up.
# If you want to set up multiple payment methods (gateways) for memberships,
# the machine name of the payment methods specified should be in this list. 
MERCHANT_ACCOUNT_NAMES = ('stripe', 'authorizenet', 'firstdatae4', 'paypal')


# ---------------------------------------------------------------------------- #
# Captcha
# ---------------------------------------------------------------------------- #

CAPTCHA_FONT_SIZE = 50
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
CAPTCHA_IMAGE_SIZE = (172,80)
CAPTCHA_OUTPUT_FORMAT = u'%(image)s <br />%(hidden_field)s %(text_field)s'

# Google reCAPTCHA
NORECAPTCHA_SITE_KEY = ''
NORECAPTCHA_SECRET_KEY = ''
NORECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
NORECAPTCHA_WIDGET_TEMPLATE = 'base/nocaptcha_recaptcha/widget.html'


# ---------------------------------------------------------------------------- #
# Django Admin Bootstrapped
# ---------------------------------------------------------------------------- #

DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

from django.contrib import messages  # noqa: E402
MESSAGE_TAGS = {
            messages.SUCCESS: 'alert-success success',
            messages.INFO: 'alert-info info',
            messages.WARNING: 'alert-warning warning',
            messages.ERROR: 'alert-danger error'
}


# ---------------------------------------------------------------------------- #
# Celery Task System
# ---------------------------------------------------------------------------- #

# import djcelery  # noqa: E402
# djcelery.setup_loader()
# BROKER_URL = "django://"
CELERY_IS_ACTIVE = False

# USE_SUBPROCESS - in places like exports and long-running
# processes that can timeout, subprocess will be used
# if this setting is True
USE_SUBPROCESS = True


# ---------------------------------------------------------------------------- #
# Haystack Search
# ---------------------------------------------------------------------------- #

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(PROJECT_ROOT, 'whoosh_index', 'main'),
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

# django-sql-explorer
EXPLORER_CONNECTIONS = { 'default': 'default' }
EXPLORER_DEFAULT_CONNECTION = 'default'
EXPLORER_UNSAFE_RENDERING = True
def EXPLORER_PERMISSION_VIEW(u):
    return u.is_superuser
def EXPLORER_PERMISSION_CHANGE(u):
    return u.is_superuser

# ---------------------------------------------------------------------------- #
# Debugging Tools
# ---------------------------------------------------------------------------- #

DEBUG_TOOLBAR_ENABLED = False
try:
    import debug_toolbar  # noqa: F401
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INSTALLED_APPS += ['debug_toolbar']
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda req: DEBUG_TOOLBAR_ENABLED,
        'SHOW_COLLAPSED': False,
    }
except ImportError:
    pass
