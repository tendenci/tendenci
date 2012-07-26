from django import template

from tendenci.core.site_settings.utils import get_setting
from django.utils.safestring import mark_safe

register = template.Library()

GLOBAL_SITE_URL = get_setting('site', 'global', 'siteurl')

def relative_to_absolute_urls(value):
    """
    Converts all relative urls to absolute urls.
    Automatically marks the strings as safe.
    e.g.
    {{ event.description|relative_to_absolute_urls }}
    """
    value = value.replace('src="/', 'src="%s/' % GLOBAL_SITE_URL)
    value = value.replace("src='/", "src='%s/" % GLOBAL_SITE_URL)
    value = value.replace('href="/', 'href="%s/' % GLOBAL_SITE_URL)
    value = value.replace("href='/", "<href='%s/" % GLOBAL_SITE_URL)
    return mark_safe(value)
    
register.filter('relative_to_absolute_urls', relative_to_absolute_urls)
