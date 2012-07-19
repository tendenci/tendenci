from django.template import Node, Library, TemplateSyntaxError, Variable

from S_P_LOW.models import S_S_CAP
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListS_P_CAPNode(ListNode):
    model = S_S_CAP
    perms = 'S_P_LOW.view_S_S_LOW'


@register.tag
def list_S_P_LOW(parser, token):
    """
    Example:

    {% list_S_P_LOW as S_P_LOW_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for S_S_LOW in S_P_LOW %}
        {{ S_S_LOW.something }}
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

    return ListS_P_CAPNode(context_var, *args, **kwargs)
