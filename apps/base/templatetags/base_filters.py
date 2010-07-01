#django
from django.template import Library
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = Library()

@register.filter(name="localize_date")
def localize_date(value, to_tz=None):
    from timezones.utils import adjust_datetime_to_timezone
    try:
        if to_tz is None:
            to_tz=settings.UI_TIME_ZONE
            
        from_tz=settings.TIME_ZONE
        
        return adjust_datetime_to_timezone(value,from_tz=from_tz,to_tz=to_tz)
    except AttributeError:
        return ''

localize_date.is_safe = True

@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

@register.filter_function
def in_group(user, arg):
    if arg:
        return arg.lower() in [dict['name'].lower() for dict in user.groups.values('name')]
    else:
        return False

@register.filter
def domain(link):
    from urlparse import urlparse
    link = urlparse(link)
    return link.hostname

@register.filter
def strip_template_tags(string):
    import re
    p = re.compile('{[#{%][^#}%]+[%}#]}')
    return re.sub(p,'',string)
    
@register.filter
@stringfilter      
def stripentities(value):
    """Strips all [X]HTML tags."""
    from django.utils.html import strip_entities
    return strip_entities(value)
stripentities.is_safe = True

@register.filter     
def format_currency(value):
    """format currency"""
    from base.utils import tcurrency
    print value
    return tcurrency(value)
format_currency.is_safe = True

@register.filter     
def date_diff(value, date_to_compare=None):
    """Compare two dates and return the difference in days"""
    import datetime
    if not isinstance(value, datetime.datetime):
        return 0
    
    if not isinstance(date_to_compare, datetime.datetime):
        date_to_compare = datetime.datetime.now()
    
    return (date_to_compare-value).days

@register.filter
def scope(object):
    return dir(object)

    
    
    