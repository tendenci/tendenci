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
    if 'toggle_template' in request.GET and is_admin(request.user):
        if request.GET.get('toggle_template'):
            request.session['toggle_template'] = request.GET.get('toggle_template')
        elif 'toggle_template' in request.session:
            del request.session['toggle_template']
    
    theme = request.session.get('theme', get_setting('module', 'theme_editor', 'theme'))
    toggle_template = request.session.get('toggle_template', 'FALSE')
    contexts['TOGGLE_TEMPLATE'] = toggle_template
    contexts['THEME'] = theme
    contexts['THEME_URL'] = '/themes/' + theme + '/'
    contexts['ACTIVE_THEME'] = get_setting('module', 'theme_editor', 'theme')
    return contexts
