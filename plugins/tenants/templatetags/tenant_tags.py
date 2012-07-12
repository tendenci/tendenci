from django.template import Library, TemplateSyntaxError

from tenants.models import Tenant, Map
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListTenantsNode(ListNode):
    model = Tenant
    perms = 'tenants.view_tenant'


@register.tag
def list_tenants(parser, token):
    """
    Example:

    {% list_tenants as tenants_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for tenant in tenants %}
        {{ tenant.something }}
    {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListTenantsNode(context_var, *args, **kwargs)


class ListMapsNode(ListNode):
    model = Map
    perms = 'maps.view_map'


@register.tag
def list_maps(parser, token):
    """
    Example:
    {% list_maps as maps [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for map in maps %}
        {{ map.name }}
    {% endfor %}

    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListMapsNode(context_var, *args, **kwargs)


@register.inclusion_tag("tenants/nav.html", takes_context=True)
def tenant_nav(context, user, obj=None):
    import re

    default_tab = 'active'
    nav_maps = Map.objects.all()

    for nav_map in nav_maps:
        nav_map.active_tab = u''
        full_path = context['request'].get_full_path()
        result = re.search('%s/$' % nav_map.slug, full_path)

        if result:
            nav_map.active_tab = 'active'
            default_tab = u''

    context.update({
        'nav_object': obj,
        'user': user,
        'nav_maps': nav_maps,
        'default_tab': default_tab,
    })
    return context


@register.inclusion_tag("tenants/search-form.html", takes_context=True)
def tenant_search(context):
    return context


@register.inclusion_tag("tenants/maps/search-form.html", takes_context=True)
def map_search(context):
    return context


@register.filter(name='height_for_width')
def height_for_width(map, width):
    return map.height_for(width)
