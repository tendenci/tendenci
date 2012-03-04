from django.conf import settings
from site_settings.utils import get_setting

from perms.utils import is_admin

def theme(request):
    contexts = {}
    if 'theme' in request.GET and is_admin(request.user):
        if request.GET.get('theme'):
            request.session['theme'] = request.GET.get('theme')
        elif 'theme' in request.session:
            del request.session['theme']
    
    theme = request.session.get('theme', get_setting('module', 'theme_editor', 'theme'))
    contexts['THEME'] = theme
    contexts['THEME_URL'] = '/themes/' + theme + '/'
    contexts['ACTIVE_THEME'] = get_setting('module', 'theme_editor', 'theme')
    return contexts
