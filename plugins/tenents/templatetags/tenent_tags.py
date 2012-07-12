from django.template import Library, TemplateSyntaxError

from tenents.models import Tenent, Map
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListTenentsNode(ListNode):
    model = Tenent
    perms = 'tenents.view_tenent'


@register.tag
def list_tenents(parser, token):
    """
    Example:

    {% list_tenents as tenents_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for tenent in tenents %}
        {{ tenent.something }}
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

    return ListTenentsNode(context_var, *args, **kwargs)


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

    return ListTenentsNode(context_var, *args, **kwargs)


@register.inclusion_tag("tenents/nav.html", takes_context=True)
def tenent_nav(context, user, job=None):
    context.update({
        'nav_object': job,
        "user": user
    })
    return context


@register.inclusion_tag("tenents/search-form.html", takes_context=True)
def tenent_search(context):
    return context


@register.inclusion_tag("tenents/maps/search-form.html", takes_context=True)
def map_search(context):
    return context


@register.filter(name='height_for_width')
def height_for_width(map, width):
    return map.height_for(width)
