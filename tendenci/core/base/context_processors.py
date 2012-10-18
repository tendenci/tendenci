from datetime import datetime

from django.conf import settings


def static_url(request):
    return {'STATIC_URL': settings.STATIC_URL, 'LOCAL_STATIC_URL': settings.LOCAL_STATIC_URL, 'STOCK_STATIC_URL': settings.STOCK_STATIC_URL, 'TINYMCE_JS_URL': settings.TINYMCE_JS_URL}


def index_update_note(request):
    return {'INDEX_UPDATE_NOTE': settings.INDEX_UPDATE_NOTE}


def today(request):
    return {'TODAY': datetime.today()}


def newrelic(request):
    try:
        import newrelic.agent
        return {
            'NEW_RELIC_HEADER': newrelic.agent.get_browser_timing_header(),
            'NEW_RELIC_FOOTER': newrelic.agent.get_browser_timing_footer(),
        }
    except ImportError:
        return {}
