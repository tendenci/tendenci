from django.template import Node, Library, TemplateSyntaxError, Variable
from django.contrib.auth.models import AnonymousUser

from base.template_tags import ListNode, parse_tag_kwargs
from testimonials.models import Testimonial

register = Library()


@register.inclusion_tag("testimonials/options.html", takes_context=True)
def testimonial_options(context, user, testimonial):
    context.update({
        "opt_object": testimonial,
        "user": user
    })
    return context


@register.inclusion_tag("testimonials/search-form.html", takes_context=True)
def testimonial_search(context):
    return context


class ListTestimonialNode(ListNode):
    model = Testimonial


@register.tag
def list_testimonials(parser, token):
    """
    Example:

    {% list_testimonials as the_testimonials user=user limit=3 %}
    {% for tsm in the_testimonials %}
        {{ cs.client }}
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

    return ListTestimonialNode(context_var, *args, **kwargs)
