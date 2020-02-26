
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Command to cache the site_url dicts for use in the sitemap.xml """

    def handle(self, *args, **options):
        from django.core.cache import cache
        from django.conf import settings
        from django.contrib.sites.models import Site
        from tendenci.apps.sitemaps.views import get_all_sitemaps

        sitemaps = dict([(cls.__name__, cls) for cls in get_all_sitemaps()])
        maps = sitemaps.values()
        for site in maps:
            if callable(site):
                site = site()
                site_key = site.__class__.__name__
            else:
                site_key = site.__name__
            sitemap_cache_key = '.'.join([settings.SITE_CACHE_KEY, 'sitemap_cache', site_key])
            site_urls = cache.get(sitemap_cache_key)
            if not isinstance(site_urls, list):
                site_urls = site.get_urls(site=Site.objects.get_current())
                cache.set(sitemap_cache_key, list(site_urls), 86400)
                print("Caching %s" % site_key)

        print("Sitemap is cached.")
