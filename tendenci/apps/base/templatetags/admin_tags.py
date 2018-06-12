from django.template import Library
from tendenci.apps.site_settings.utils import get_setting

register = Library()

@register.filter
def check_enabled(value):
    # Only check if it's false since other packages and
    # Django apps (like auth_user) may not use our settings
    return not get_setting('module', value.lower(), 'enabled') is False


# admin tags derived from django_admin_bootstrapped
@register.filter(name="tadmin_form_line_column_width")
def tadmin_form_line_column_width(line):
    try:
        width = len(list(line))
        value = 12 // width
        return value
    except:
        return 12
