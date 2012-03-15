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
    try:
        nav = Nav.objects.get(id=nav_id)
    except:
        return None
    context.update({
        "nav": nav,
        "items": nav.top_items,
    })
    return context

@register.inclusion_tag("navs/load_nav.html", takes_context=True)
def load_nav(context, nav_id):
    """
    Renders the nav and its nav items.
    This will call nav_item that will call itself recursively nesting 
    the subnavs
    """
    try:
        nav = Nav.objects.get(id=nav_id)
    except:
        return None
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


class ListNavNode(ListNode):
    model = Nav
    perms = 'navs.view_nav'


@register.tag
def list_navs(parser, token):
    """
    Used to pull a list of :model:`navs.Nav` items.

    Usage::

        {% list_case_studies as [varname] [options] %}

    Be sure the [varname] has a specific name like ``case_studies_sidebar`` or 
    ``case_studies_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:
    
        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: ID**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_navs as nav_list limit=5 tags="cool" %}
        {% for nav in nav_list %}
            {% nav nav %}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = 'pk'

    return ListNavNode(context_var, *args, **kwargs)
