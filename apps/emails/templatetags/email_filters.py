from django import template

from site_settings.utils import get_setting

register = template.Library()

GLOBAL_SITE_URL = get_setting('site', 'global', 'siteurl')

print GLOBAL_SITE_URL

def relative_to_absolute_urls(value):
    """
    Converts all relative urls to absolute urls
    """
    value = value.replace('src="/', 'src="%s/' % GLOBAL_SITE_URL)
    value = value.replace("src='/", "src='%s/" % GLOBAL_SITE_URL)
    value = value.replace('href="/', 'href="%s/' % GLOBAL_SITE_URL)
    value = value.replace("href='/", "<href='%s/" % GLOBAL_SITE_URL)
    return value
    
register.filter('relative_to_absolute_urls', relative_to_absolute_urls)
