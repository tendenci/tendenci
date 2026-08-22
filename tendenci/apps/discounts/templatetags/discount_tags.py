from django.conf import settings
from django.template import Library
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils import timezone


register = Library()


@register.inclusion_tag("discounts/options.html", takes_context=True)
def discount_options(context, user, discount):
    context.update({
        "opt_object": discount,
        "user": user
    })
    return context


@register.inclusion_tag("discounts/nav.html", takes_context=True)
def discount_nav(context, user, discount=None):
    context.update({
        "nav_object": discount,
        "user": user
    })
    return context


@register.inclusion_tag("discounts/search-form.html", takes_context=True)
def discount_search(context):
    return context


@register.inclusion_tag("discounts/top_nav_items.html", takes_context=True)
def discount_current_app(context, user, discount=None):
    context.update({
        "app_object": discount,
        "user": user
    })
    return context


@register.simple_tag
def discount_expiration(obj):
    t = '<span class="status-%s">%s</span>'

    if not obj.never_expires:
        if obj.end_dt < timezone.now():
            value = t % ('inactive', f'Expired {date_format(obj.end_dt, "DATETIME_FORMAT")}')
        else:
            if obj.start_dt > timezone.now():
                value = t % ('inactive',f'Starts {date_format(obj.start_dt, "DATETIME_FORMAT")}' )
            else:
                value = t % ('active', f'Expires {date_format(obj.end_dt, "DATETIME_FORMAT")}')
    else:
        value = t % ('active', "Never Expires")

    return mark_safe(value)
