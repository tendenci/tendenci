from django.template import Node, Library, TemplateSyntaxError, Variable

from plugs.models import Plug
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListPlugsNode(ListNode):
    model = Plug


@register.tag
def list_plugs(parser, token):
    """
    Example:

    {% list_plugs as plugs_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for plug in plugs %}
        {{ plug.something }}
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

    return ListPlugsNode(context_var, *args, **kwargs)
