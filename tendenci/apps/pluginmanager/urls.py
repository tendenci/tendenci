from django.conf.urls.defaults import patterns, include
from tendenci.apps.pluginmanager.utils import get_addons


def get_url_patterns():
    from django.conf import settings
    items = []
    addons = get_addons(settings.INSTALLED_APPS)
    for addon in addons:
        items.append((r'', include('%s.urls' % addon,)))
    return patterns('', *items)
    pass
