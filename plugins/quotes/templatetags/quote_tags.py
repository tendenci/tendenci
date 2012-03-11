from django.template import Node, Library, TemplateSyntaxError, Variable

from quotes.models import Quote
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListQuotesNode(ListNode):
    model = Quote
    perms = 'quotes.view_quote'


@register.tag
def list_quotes(parser, token):
    """
    Used to pull a list of :model:`quotes.Quote` items.

    Usage::

        {% list_quotes as [varname] [options] %}

    Be sure the [varname] has a specific name like ``quotes_sidebar`` or 
    ``quotes_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:
    
        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Added**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_quotes as quotes_list limit=5 tags="cool" %}
        {% for quote in quotes_list %}
            {{ quote.quote }}
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

    return ListQuotesNode(context_var, *args, **kwargs)
