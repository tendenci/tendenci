from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
from attornies.models import Attorney

register = Library()


@register.inclusion_tag("attornies/options.html", takes_context=True)
def attornies_options(context, user, attorney):
    context.update({
        "opt_object": attorney,
        "user": user
    })
    return context


@register.inclusion_tag("attornies/search-form.html", takes_context=True)
def attornies_search(context):
    return context


class ListAttorneyNode(ListNode):
    model = Attorney


@register.tag
def list_attornies(parser, token):
    """
    Example:

    {% list_attornies as the_attornies user=user limit=3 %}
    {% for attorney in the_attornies %}
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
