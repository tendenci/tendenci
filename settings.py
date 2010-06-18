import os.path
import sys

# Paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
APPS_PATH = os.path.join(PROJECT_ROOT, 'apps')
sys.path.insert(0, APPS_PATH)

DEBUG = False
TEMPLATE_DEBUG = DEBUG
SITE_THEME = "tendenci"

ADMINS = (
    ('Glen Zangirolami', 'gzangirolami@schipul.com'),
	('Eloy Zuniga Jr.', 'ezuniga@schipul.com'),
    ('Jennifer Ulmer', 'julmer@schipul.com'),
    ('Jenny Qian', 'jqian@schipul.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tendenci50',
        'USER': 'tendenci50',
        'PASSWORD': 'Ly89e1c',
        'HOST': 'NTSERVER17',
        'PORT': '3306',
    }
}
# email
EMAIL_HOST = '4.78.3.131'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'jqian@schipul.com'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en-us', u'English'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

THEME_ROOT = os.path.join(PROJECT_ROOT, 'themes', SITE_THEME)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/media/'

# Absolute path to the directory that holds static media.
STATIC_ROOT = os.path.join(MEDIA_ROOT, 'static')

# URL that handles the media served from STATIC_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
STATIC_URL = '/site_media/static/'

# Avatar default URL, no Gravatars
AVATAR_GRAVATAR_BACKUP = False
AVATAR_DEFAULT_URL = STATIC_URL + '/images/icons/default-user-80.jpg'
AUTO_GENERATE_AVATAR_SIZES = (128, 80, 48,)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 's$6*!=m$t0__=51^w@_tbazonjm4+fg@0+ic#bx^3rj)zc$a6i'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'swfupload.middleware.SWFUploadMiddleware',
    #'swfupload.middleware.MediaUploadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'perms.middleware.ImpersonationMiddleware',
    'base.middleware.Http403Middleware',
)

ROOT_URLCONF = 'Tendenci50.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "themes", SITE_THEME, "templates"),
    os.path.join(PROJECT_ROOT, "templates"),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    
    # tendenci context processors
    'theme.context_processors.theme',
    'site_settings.context_processors.settings',
    'base.context_processors.static_url'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',

    # third party applications
    'pagination',
    'photologue',
    'tagging',
    'registration',
    'avatar',
    'tinymce',
    'haystack',
    
    # tendenci applications
    'base',
    'perms',
    'profiles',
    'articles',
    'news',
    'stories',
    'pages',
    'photos',
    'base',
    'entities',
    'locations',
    'site_settings',
    'user_groups',
    #'make_payments',
    #'invoices',
    'files',
    'event_logs',
    'robots',
    'theme_editor',
    'jobs',
)

# This is the number of days users will have to activate their
# accounts after registering. If a user does not activate within
# that period, the account will remain permanently inactive and may
#be deleted by maintenance scripts provided in django-registration.
ACCOUNT_ACTIVATION_DAYS = 7 

LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = 'profiles.Profile'
AUTHENTICATION_BACKENDS = (
    'perms.backend.ObjectPermBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# -------------------------------------- #
#    TINYMCE
# -------------------------------------- #
TINYMCE_JS_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static', 'tinymce')
TINYMCE_JS_URL = STATIC_URL + 'tinymce/tiny_mce.js'
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "stormeimage,table,paste,searchreplace,inlinepopups,tabfocus,fullscreen,media,spellchecker",
    'gecko_spellcheck': False,
    'theme': "advanced",
    'theme_advanced_buttons1': "bold,italic,underline,strikethrough,|,bullist,numlist,|,justifyleft,justifycenter,justifyright,|,link,unlink,|,image,|,pagebreak,fullscreen,code",
    'theme_advanced_buttons2': "formatselect,underline,justifyfull,forecolor,|,pastetext,pasteword,removeformat,media,charmap,|,outdent,indent,|,undo,redo",
    'theme_advanced_buttons3': "",
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "left",
    'theme_advanced_statusbar_location': "bottom",
    'theme_advanced_resizing' : True,
    'theme_advanced_resize_horizontal': True,
    'dialog_type': "modal",
    'tab_focus': ":prev, :next",
    'urlconverter_callback': 'tinymce_urlconverter',
    'apply_source_formatting' : False,
}



# -------------------------------------- #
# CACHING
# -------------------------------------- #
CACHE_DIR = PROJECT_ROOT + "/cache"
CACHE_BACKEND = "file://" + CACHE_DIR + "?timeout=604800" # 7 days

# --------------------------------------#
# Hackstack Search
# --------------------------------------#
HAYSTACK_SITECONF = 'search'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8000/tendenci50/'
HAYSTACK_SOLR_TIMEOUT = 60
HAYSTACK_INCLUDED_APPS = ('article','page','news','story')

# local settings for development
try:
    from local_settings import *
except ImportError:
    pass

