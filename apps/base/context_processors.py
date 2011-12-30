from django.conf import settings
from datetime import datetime

def static_url(request):
    return {'STATIC_URL': settings.STATIC_URL}

def index_update_note(request):
    return {'INDEX_UPDATE_NOTE': settings.INDEX_UPDATE_NOTE}

def today(request):
    return {'TODAY': datetime.today()}
