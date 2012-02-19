from django.template import Node, Library, TemplateSyntaxError, Variable

from lots.models import Lot
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()

class ListLotsNode(ListNode):
    model = Lot

@register.tag
def list_lots(parser, token):
    """
    Example:

    {% list_lots as lots_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for lot in lots %}
        {{ lot.something }}
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

    return ListLotsNode(context_var, *args, **kwargs)

@register.inclusion_tag("lots/nav.html", takes_context=True)
def lot_nav(context, user, job=None):
    context.update({
        'nav_object': job,
        "user": user
    })
    return context

@register.inclusion_tag("lots/search-form.html", takes_context=True)
def lot_search(context):
    return context
    
@register.inclusion_tag("lots/maps/search-form.html", takes_context=True)
def map_search(context):
    return context

@register.filter(name='height_for_width')
def height_for_width(value, width):
    return value.height_for(width)
