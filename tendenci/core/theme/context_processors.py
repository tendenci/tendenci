from django.conf import settings
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.theme.utils import get_theme_info
from django.core.cache import cache


def theme(request):
    contexts = {}
    if 'theme' in request.GET and request.user.profile.is_superuser:
        if request.GET.get('theme'):
            request.session['theme'] = request.GET.get('theme')
        elif 'theme' in request.session:
            del request.session['theme']

    if 'toggle_template' in request.GET:
        contexts['TOGGLE_TEMPLATE'] = True

    # get the  active theme from cache
    active_theme = cache.get('active_theme', None)
    if not active_theme:
        active_theme = get_setting('module', 'theme_editor', 'theme')
        cache.set('active_theme', active_theme, 120)

    contexts['ACTIVE_THEME'] = active_theme

    theme = request.session.get('theme', contexts['ACTIVE_THEME'])
    contexts['THEME'] = theme

    if settings.USE_S3_STORAGE:
        contexts['THEME_URL'] = '%s/%s/%s/themes/%s/' % (settings.S3_ROOT_URL,
            settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_LOCATION, theme)
    else:
        contexts['THEME_URL'] = '/themes/' + theme + '/'

    contexts['LOCAL_THEME_URL'] = '/themes/' + theme + '/'

    theme_info = cache.get('theme_info', None)
    if not theme_info:
        theme_info = get_theme_info(theme)
        cache.set('theme_info', theme_info, 120)

    contexts['THEME_INFO'] = theme_info

    return contexts
