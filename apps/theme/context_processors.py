from django.conf import settings
from site_settings.utils import get_setting

def theme(request):
    contexts = {}
    theme = request.GET.get('theme', get_setting('module', 'theme_editor', 'theme'))
    contexts['THEME'] = theme
    contexts['THEME_URL'] = '/themes/' + theme + '/'
    return contexts
