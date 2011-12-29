from django.template import Node, Library, TemplateSyntaxError, Variable

from museums.models import Museum
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListMuseumsNode(ListNode):
    model = Museum


@register.tag
def list_museums(parser, token):
    """
    Example:

    {% list_museums as museums_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for museum in museums %}
        {{ museum.something }}
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

    return ListMuseumsNode(context_var, *args, **kwargs)

@register.inclusion_tag("museums/search-form.html", takes_context=True)
def museum_search(context):
    return context
