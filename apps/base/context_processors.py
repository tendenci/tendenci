from django.conf import settings

def static_url(request):
    return {'STATIC_URL': settings.STATIC_URL}