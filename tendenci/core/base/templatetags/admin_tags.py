from django.template import Library
from tendenci.core.site_settings.utils import get_setting

register = Library()

@register.filter
def check_enabled(value):
    # Only check if it's false since other packages and
    # Django apps (like auth_user) may not use our settings
    if get_setting('module', value.lower(), 'enabled') == False:
        return False
    return True
