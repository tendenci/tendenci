from django.template import Node, Library, TemplateSyntaxError, Variable

from quotes.models import Quote
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListQuotesNode(ListNode):
    model = Quote


@register.tag
def list_quotes(parser, token):
    """
    Example:

    {% list_quotes as quotes_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for quote in quotes %}
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
