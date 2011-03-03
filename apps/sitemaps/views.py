'''
Created on 28-02-2011

@author: hpolloni
'''

from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from sitemaps import TendenciSitemap


_sitemap_cache = []
def get_all_sitemaps():
    for app in settings.INSTALLED_APPS:
        _try_import(app + '.feeds')
    return TendenciSitemap.__subclasses__()

def _try_import(module):
    try:
        __import__(module)
    except ImportError, e:
        pass

def create_sitemap(request):
    sitemap_classes = get_all_sitemaps()
    #print "Found %d sitemap classes" % len(sitemap_classes)
    #for cls in sitemap_classes:
    #    print cls.__name__
    sitemaps = dict([(cls.__name__, cls) for cls in sitemap_classes])
    #print str(sitemaps)
    return sitemap(request, sitemaps)


