from django.conf import settings
from tendenci.core.site_settings.utils import get_setting

def theme(request):
    contexts = {}
    if 'theme' in request.GET and request.user.profile.is_superuser:
        if request.GET.get('theme'):
            request.session['theme'] = request.GET.get('theme')
        elif 'theme' in request.session:
            del request.session['theme']
    if 'toggle_template' in request.GET and request.user.profile.is_superuser:
        if request.GET.get('toggle_template'):
            request.session['toggle_template'] = request.GET.get('toggle_template')
        elif 'toggle_template' in request.session:
            del request.session['toggle_template']
    
    theme = request.session.get('theme', get_setting('module', 'theme_editor', 'theme'))
    toggle_template = request.session.get('toggle_template', 'FALSE')
    contexts['TOGGLE_TEMPLATE'] = toggle_template
    contexts['THEME'] = theme
    
    if settings.USE_S3_STORAGE:
        contexts['THEME_URL'] = '%s/%s/%s/themes/%s/' % (settings.S3_ROOT_URL, 
                                                         settings.AWS_STORAGE_BUCKET_NAME, 
                                                         settings.AWS_LOCATION,
                                                         theme)
    else:
        contexts['THEME_URL'] = '/themes/' + theme + '/'
    contexts['LOCAL_THEME_URL'] = '/themes/' + theme + '/'
        
    contexts['ACTIVE_THEME'] = get_setting('module', 'theme_editor', 'theme')
    return contexts
