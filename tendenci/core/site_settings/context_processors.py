from django.core.cache import cache
from django.conf import settings as d_settings
from django.template import Context, Template

from tendenci import __version__ as version
from tendenci.core.site_settings.models import Setting
from tendenci.core.site_settings.cache import SETTING_PRE_KEY

def settings(request):
    """Context processor for settings
    """
    key = [d_settings.CACHE_PRE_KEY, SETTING_PRE_KEY, 'all']
    key = '.'.join(key)

    settings = cache.get(key)
    if not settings:
        settings = Setting.objects.all()
        is_set = cache.add(key, settings)
        if not is_set:
            cache.set(key, settings)

    contexts = {}
    for setting in settings:
        context_key = [setting.scope, setting.scope_category,
                       setting.name]
        context_key = '_'.join(context_key)

        value = setting.get_value().strip()

        if setting.data_type == 'boolean':
            value = value[0].lower() == 't'
        if setting.data_type == 'int':
            if value.strip(): value = int(value.strip())
            else: value = 0 # default to 0
        # Handle context for the social_media addon's
        # contact_message setting
        if setting.name == 'contact_message':
            page_url = request.build_absolute_uri()
            message_context = {'page_url': page_url}
            message_context = Context(message_context)
            message_template = Template(value)
            value = message_template.render(message_context)

        contexts[context_key.upper()] = value

    contexts['TENDENCI_VERSION'] = version

    contexts['USE_I18N'] = d_settings.USE_I18N

    return contexts
