from django.conf import settings
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.utils import get_theme_info


def theme(request):
    contexts = {}
    if 'theme' in request.GET and request.user.profile.is_superuser:
        if request.GET.get('theme'):
            request.session['theme'] = request.GET.get('theme')
        elif 'theme' in request.session:
            del request.session['theme']

    if 'toggle_template' in request.GET:
        contexts['TOGGLE_TEMPLATE'] = True

    contexts['ACTIVE_THEME'] = get_setting('module', 'theme_editor', 'theme')
    theme = request.session.get('theme', contexts['ACTIVE_THEME'])
    contexts['THEME'] = theme

    if settings.USE_S3_STORAGE:
        contexts['THEME_URL'] = '%s/%s/%s/themes/%s/' % (settings.S3_ROOT_URL,
            settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_LOCATION, theme)
    else:
        contexts['THEME_URL'] = '/themes/' + theme + '/'

    contexts['LOCAL_THEME_URL'] = '/themes/' + theme + '/'


    contexts['THEME_INFO'] = get_theme_info(theme)

    return contexts
