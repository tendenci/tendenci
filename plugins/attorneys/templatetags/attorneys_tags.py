from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
from attorneys.models import Attorney

register = Library()


@register.inclusion_tag("attorneys/options.html", takes_context=True)
def attorneys_options(context, user, attorney):
    context.update({
        "opt_object": attorney,
        "user": user
    })
    return context


@register.inclusion_tag("attorneys/search-form.html", takes_context=True)
def attorneys_search(context):
    return context


class ListAttorneyNode(ListNode):
    model = Attorney


@register.tag
def list_attorneys(parser, token):
    """
    Example:

    {% list_attorneys as attorneys user=user limit=3 %}
    {% for attorney in attorneys %}
        {{ attorney.name }}
    {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListAttorneyNode(context_var, *args, **kwargs)
