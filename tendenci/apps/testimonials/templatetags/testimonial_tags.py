from django.template import Library, TemplateSyntaxError

from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.testimonials.models import Testimonial

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
    perms = 'testimonials.view_testimonial'

@register.inclusion_tag("testimonials/top_nav_items.html", takes_context=True)
def testimonial_current_app(context, user, testimonial=None):
    context.update({
        "app_object": testimonial,
        "user": user
    })
    return context

@register.tag
def list_testimonials(parser, token):
    """
    Used to pull a list of :model:`testimonials.Testimonial` items.

    Usage::

        {% list_testimonials as [varname] [options] %}

    Be sure the [varname] has a specific name like ``testimonials_sidebar`` or
    ``testimonials_list``. Options can be used as [option]=[value]. Wrap text values
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

        {% list_testimonials as testimonials_list limit=5 tags="cool" %}
        {% for testimonial in testimonials_list %}
            {{ testimonial.title }}
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
