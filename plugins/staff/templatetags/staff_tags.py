from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
from staff.models import Staff

register = Library()


@register.inclusion_tag("staff/options.html", takes_context=True)
def staff_options(context, user, staff):
    context.update({
        "opt_object": staff,
        "user": user
    })
    return context


@register.inclusion_tag("staff/search-form.html", takes_context=True)
def staff_search(context):
    return context


class ListStaffNode(ListNode):
    model = Staff


@register.tag
def list_staff(parser, token):
    """
    Example:

    {% list_staff as the_staff user=user limit=3 %}
    {% for staff_member in the_staff %}
        {{ staff_member.name }}
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

    return ListStaffNode(context_var, *args, **kwargs)
