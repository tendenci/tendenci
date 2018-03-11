from django.template import Library, TemplateSyntaxError

from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.staff.models import Staff

register = Library()


@register.inclusion_tag("staff/top_nav_items.html", takes_context=True)
def staff_current_app(context, user, staff=None):
    context.update({
        "app_object": staff,
        "user": user
    })
    return context


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
    perms = 'staff.view_staff'


@register.tag
def list_staff(parser, token):
    """
    Used to pull a list of :model:`staff.Staff` items.

    Usage::

        {% list_staff as [varname] [options] %}

    Be sure the [varname] has a specific name like ``staff_sidebar`` or
    ``staff_list``. Options can be used as [option]=[value]. Wrap text values
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

        {% list_staff as staff_list limit=5 tags="cool" %}
        {% for staff_person in staff_list %}
            {{ staff_person.name }}
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
