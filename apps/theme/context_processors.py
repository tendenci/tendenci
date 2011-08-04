from django.conf import settings
from site_settings.utils import get_setting

def theme(request):
    contexts = {}
    contexts['THEME_URL'] = '/themes/' + get_setting('module', 'theme_editor', 'theme') + '/'
    return contexts
