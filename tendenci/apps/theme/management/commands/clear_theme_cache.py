from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache


class Command(BaseCommand):
    """
    If theme files are served on an external server, such as AWS S3,
    the theme files contents are cached and the cache keys are added
    to a list that is also cached. This command clears that list, so
    that theme files are then re-cached.

    A usecase for this would be whenever a new theme is uploaded to the remote storage.

    Usage: manage.py clear_theme_cache
    """

    def handle(self, *args, **options):
        cache_group_key = "%s.theme_files_cache_list" % settings.SITE_CACHE_KEY
        cache_group_list = cache.get(cache_group_key)

        if cache_group_list:  # protects against NoneType object
            for key in cache_group_list:
                cache.delete(key)
            cache.set(cache_group_key, [])
