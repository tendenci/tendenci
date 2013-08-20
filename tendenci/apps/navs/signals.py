from django.core.cache import cache
from django.conf import settings

from tendenci.apps.navs.cache import NAV_PRE_KEY


def update_nav_links(sender, instance, **kwargs):
    # NavItem imported here to avoid import conflict
    from tendenci.apps.navs.models import NavItem

    page_pk = instance.pk
    nav_items = NavItem.objects.filter(page_id=page_pk)
    for item in nav_items:
        if item.url != instance.get_absolute_url():
            item.url = instance.get_absolute_url()
            item.save()
            nav = item.nav
            keys = [settings.CACHE_PRE_KEY, NAV_PRE_KEY, str(nav.id)]
            key = '.'.join(keys)
            cache.delete(key)
