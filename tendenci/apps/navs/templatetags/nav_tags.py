from django.template import Library, TemplateSyntaxError, Variable, Node
from django.utils.translation import ugettext_lazy as _
from tendenci.core.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.core.perms.utils import get_query_filters
from django.contrib.auth.models import AnonymousUser, User
from tendenci.apps.navs.models import Nav
from tendenci.apps.navs.utils import get_nav, cache_nav

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
    user = AnonymousUser()

    if 'user' in context:
        if isinstance(context['user'], User):
            user = context['user']

    try:
        nav_id = Variable(nav_id)
        nav_id = nav_id.resolve(context)
    except:
        pass

    try:
        filters = get_query_filters(user, 'navs.view_nav')
        navs = Nav.objects.filter(filters).filter(id=nav_id)
        if user.is_authenticated():
            if not user.profile.is_superuser:
                navs = navs.distinct()
        nav = navs[0]
    except:
        return None
    context.update({
        "nav": nav,
        "items": nav.top_items,
    })
    return context

@register.inclusion_tag("navs/load_nav.html", takes_context=True)
def load_nav(context, nav_id, show_title=False):
    """
    Renders the nav and its nav items.
    This will call nav_item that will call itself recursively nesting
    the subnavs
    """
    # No perms check because load_nav is only called by the other tags
    try:
        nav = Nav.objects.get(id=nav_id)
    except:
        return None
    context.update({
        "nav": nav,
        "items": nav.top_items,
        "show_title": show_title,
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
def nav(context, nav_id, show_title=False):

    """
    Renders the nav from cache
    if not will use the navigation tag for rendering the nav
    """
    user = AnonymousUser()

    if 'user' in context:
        if isinstance(context['user'], User):
            user = context['user']

    try:
        nav_id = Variable(nav_id)
        nav_id = nav_id.resolve(context)
    except:
        pass

    try:
        filters = get_query_filters(user, 'navs.view_nav')
        navs = Nav.objects.filter(filters).filter(id=nav_id)
        if user.is_authenticated():
            if not user.profile.is_superuser:
                navs = navs.distinct()

        nav_object = navs[0]
        nav = get_nav(nav_object.pk)
        if not nav:
            nav = cache_nav(nav_object, show_title)
    except:
        return None

    context.update({
        "cached": nav,
        "nav_id": nav_id,
        "show_title": show_title,
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
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = 'pk'

    return ListNavNode(context_var, *args, **kwargs)


class GetNavNode(Node):
    def __init__(self, pk, context_var):
        self.pk = pk
        self.context_var = context_var

    def render(self, context):
        user = AnonymousUser()

        if 'user' in context:
            if isinstance(context['user'], User):
                user = context['user']

        try:
            pk = Variable(self.pk)
            pk = pk.resolve(context)
        except:
            pk = self.pk

        try:
            filters = get_query_filters(user, 'navs.view_nav')
            nav = Nav.objects.filter(filters).filter(pk=pk)
            if user.is_authenticated():
                if not user.profile.is_superuser:
                    nav = nav.distinct()

            context[self.context_var] = nav[0]
        except:
            pass

        return unicode()


@register.tag
def nav_object(parser, token):
    """
    Get a nav object and return it to [varname] in the context

    Usage::

        {% nav_object 2 as [varname] %}
    """
    bits = token.split_contents()

    context_var = bits[3]
    pk = bits[1]

    if len(bits) < 4:
        message = "'%s' tag requires at least 3 parameters" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[2] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    return GetNavNode(pk, context_var)
