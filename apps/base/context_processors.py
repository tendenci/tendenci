from django.conf import settings

def static_url(request):
    return {'STATIC_URL': settings.STATIC_URL}

def index_update_note(request):
    return {'INDEX_UPDATE_NOTE': settings.INDEX_UPDATE_NOTE}
