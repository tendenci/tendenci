from datetime import datetime
from django.template import Library, TemplateSyntaxError, Variable
from base.template_tags import ListNode, parse_tag_kwargs
from navs.models import Nav
from navs.utils import get_nav, cache_nav

register = Library()

@register.inclusion_tag("navs/options.html", takes_context=True)
def nav_options(context, user, nav):
    context.update({
        "opt_object": nav,
        "user": user
    })
    return context

@register.inclusion_tag("navs/nav.html", takes_context=True)
def nav_nav(context, user, nav=None):
    context.update({
        "nav_object": nav,
        "user": user
    })
    return context

@register.inclusion_tag("navs/search-form.html", takes_context=True)
def nav_search(context):
    return context
    
@register.inclusion_tag("navs/navigation.html", takes_context=True)
def navigation(context, nav_id):
    """
    Renders the nav and its nav items.
    This will call nav_item that will call itself recursively nesting 
    the subnavs
    """
    nav = Nav.objects.get(id=nav_id)
    context.update({
        "nav": nav,
        "items": nav.top_items,
    })
    return context

@register.inclusion_tag("navs/navigation_item.html", takes_context=True)
def nav_item(context, item):
    """
        Renders a nav item and its children.
    """
    context.update({
        "item": item,
    })
    return context

@register.inclusion_tag("navs/cached_nav.html", takes_context=True)
def nav(context, nav_id):
    """
    Renders the nav from cache
    if not will use the navigation tag for rendering the nav
    """
    nav = get_nav(nav_id)
    if not nav:
        #cache the nav if its not cached
        cache_nav(Nav.objects.get(id=nav_id))
    context.update({
        "cached": nav,
        "nav_id": nav_id,
    })
    return context
