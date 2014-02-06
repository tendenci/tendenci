from datetime import datetime

from django.conf import settings

from tendenci.core.site_settings.utils import get_setting


def static_url(request):
    return {'STATIC_URL': settings.STATIC_URL, 'LOCAL_STATIC_URL': settings.LOCAL_STATIC_URL, 'STOCK_STATIC_URL': settings.STOCK_STATIC_URL, 'TINYMCE_JS_URL': settings.TINYMCE_JS_URL}


def index_update_note(request):
    return {'INDEX_UPDATE_NOTE': settings.INDEX_UPDATE_NOTE}


def today(request):
    return {'TODAY': datetime.today()}


def newrelic(request):
    """ newrelic removed due to increase of timeouts """
    return {
        'NEW_RELIC_HEADER': "",
        'NEW_RELIC_FOOTER': "",
    }

def site_admin_email(request):
    return {'SITE_ADMIN_EMAIL': get_setting('site', 'global', 'admincontactemail')}
