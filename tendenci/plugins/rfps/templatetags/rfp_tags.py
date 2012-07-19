from django.template import Node, Library, TemplateSyntaxError, Variable

from rfps.models import RFP
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListRFPsNode(ListNode):
    model = RFP
    perms = 'rfps.view_rfp'

@register.inclusion_tag("rfps/nav.html", takes_context=True)
def rfp_nav(context, user, rfp=None):
    context.update({
        "nav_object": rfp,
        "user": user
    })
    return context

@register.tag
def list_rfps(parser, token):
    """
    Example:

    {% list_rfps as rfps_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for rfp in rfps %}
        {{ rfp.something }}
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

    return ListRFPsNode(context_var, *args, **kwargs)

@register.inclusion_tag("rfps/search-form.html", takes_context=True)
def rfp_search(context):
    return context
