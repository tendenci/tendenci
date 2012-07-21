from django.conf.urls.defaults import patterns, include
from pluginmanager.settings import get_apps

def get_url_patterns():
    from django.conf import settings
    items = []
    apps = get_apps(settings.LOCAL_ROOT)
    for plugin in apps:
        if plugin['is_installed'] and plugin['is_enabled']:
            items.append((r'', include('%s.urls' % plugin['package'],)))
    return patterns('', *items)
