from django.template import Library
from tendenci.core.site_settings.utils import get_setting

register = Library()

@register.filter
def check_enabled(value):
    return get_setting('module', value.lower(), 'enabled')
