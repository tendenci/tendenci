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
    perms = 'attorneys.view_attorney'


@register.tag
def list_attorneys(parser, token):
    """
    Used to pull a list of :model:`attorneys.Attorney` items.

    Usage::

        {% list_attorneys as [varname] [options] %}

    Be sure the [varname] has a specific name like ``attorneys_sidebar`` or 
    ``attorneys_list``. Options can be used as [option]=[value]. Wrap text values
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

        {% list_attorneys as attorneys_list limit=5 tags="cool" %}
        {% for attorney in attorneys_list %}
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
