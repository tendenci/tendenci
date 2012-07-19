from django.conf import settings
from datetime import datetime

def static_url(request):
    return {'STATIC_URL': settings.STATIC_URL, 'LOCAL_STATIC_URL': settings.LOCAL_STATIC_URL, 'TINYMCE_JS_URL': settings.TINYMCE_JS_URL}

def index_update_note(request):
    return {'INDEX_UPDATE_NOTE': settings.INDEX_UPDATE_NOTE}

def today(request):
    return {'TODAY': datetime.today()}
