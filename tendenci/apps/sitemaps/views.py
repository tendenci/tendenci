'''
Created on 28-02-2011

@author: hpolloni
'''
import subprocess

from django.contrib.sites.models import get_current_site
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.core.cache import cache
from tendenci.apps.sitemaps import TendenciSitemap
from tendenci.apps.site_settings.utils import get_setting


_sitemap_cache = []


def get_all_sitemaps():
    # commenting out the following 2 lines because it has no effect to the result.
#    for app in settings.INSTALLED_APPS:
#        _try_import(app + '.feeds')
    sitemap_classes = TendenciSitemap.__subclasses__()
    for sitemap_class in sitemap_classes:
        if not get_setting('module', sitemap_class.__module__.split('.')[-2], 'enabled'):
            sitemap_classes.remove(sitemap_class)
    return sitemap_classes


def _try_import(module):
    try:
        __import__(module)
    except ImportError, e:
        pass


def create_sitemap(request):
    sitemap_classes = get_all_sitemaps()
    sitemaps = dict([(cls.__name__, cls) for cls in sitemap_classes])
    return sitemap(request, sitemaps)


def sitemap(request, sitemaps, section=None,
            template_name='sitemap.xml', mimetype='application/xml'):
    #req_protocol = 'https' if request.is_secure() else 'http'
    req_protocol = get_setting('site', 'global', 'siteurl').split(':')[0]
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404(_("No sitemap available for section: %r" % section))
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    urls = []
    cached = False
    for site in maps:
        try:
            if callable(site):
                site = site()
                site_key = site.__class__.__name__
            else:
                site_key = site.__name__
            # Cache the sitemap urls
            sitemap_cache_key = '.'.join([settings.SITE_CACHE_KEY, 'sitemap_cache', site_key, req_protocol])
            site_urls = cache.get(sitemap_cache_key)
            if not isinstance(site_urls, list):
                if not cached:
                    subprocess.Popen(['python', 'manage.py', 'sitemap_cache'])
                    cached = True
                site_urls = site.get_urls(page=page, site=req_site,
                                          protocol=req_protocol)
                cache.set(sitemap_cache_key, list(site_urls), 86400)
            urls.extend(site_urls)
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=mimetype)
