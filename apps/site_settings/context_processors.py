from django.core.cache import cache

from site_settings.models import Setting
from site_settings.cache import SETTING_PRE_KEY

def settings(request):
    """
        Context processor for settings
    """
    key = [SETTING_PRE_KEY, 'all.settings']
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
        contexts[context_key.upper()] = setting.value
        
    return contexts