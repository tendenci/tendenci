from django.conf import settings
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.theme.utils import get_theme_info


def theme(request):
    context = {}

    context['ACTIVE_THEME'] = get_setting('module', 'theme_editor', 'theme')
    theme = request.session.get('theme', context['ACTIVE_THEME'])
    context['THEME'] = theme

    if settings.USE_S3_STORAGE:
        context['THEME_URL'] = '%s/%s/%s/themes/%s/' % (settings.S3_ROOT_URL,
            settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_LOCATION, theme)
    else:
        context['THEME_URL'] = '/themes/' + theme + '/'
    context['LOCAL_THEME_URL'] = '/themes/' + theme + '/'

    context['THEME_INFO'] = get_theme_info(theme)

    return context
