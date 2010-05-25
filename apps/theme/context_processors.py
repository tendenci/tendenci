from django.conf import settings

def theme(request):
    contexts = {}
    contexts['THEME_URL'] = '/themes/' + settings.SITE_THEME + '/'
    return contexts