from datetime import datetime

from django.template import Library

register = Library()


@register.inclusion_tag("newsletters/nav.html", takes_context=True)
def newsletter_nav(context, user, newsletter=None):
    context.update({
        "nav_object": newsletter,
        "user": user
    })
    return context


@register.inclusion_tag("newsletters/top_nav_items.html", takes_context=True)
def newsletter_current_app(context, user, newsletter=None):
    context.update({
        "app_object": newsletter,
        "user": user
    })
    return context


