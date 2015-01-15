from django.template import Library, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.locations.models import Location


register = Library()


@register.inclusion_tag("locations/options.html", takes_context=True)
def location_options(context, user, location):
    context.update({
        "opt_object": location,
        "user": user
    })
    return context


@register.inclusion_tag("locations/nav.html", takes_context=True)
def location_nav(context, user, location=None):
    context.update({
        "nav_object": location,
        "user": user
    })
    return context


@register.inclusion_tag("locations/search-form.html", takes_context=True)
def location_search(context):
    return context


@register.inclusion_tag("locations/top_nav_items.html", takes_context=True)
def location_current_app(context, user, location=None):
    context.update({
        "app_object": location,
        "user": user
    })
    return context


class ListLocationNode(ListNode):
    model = Location
    perms = 'locations.view_location'


@register.tag
def list_locations(parser, token):
    """
    Used to pull a list of :model:`locations.Location` items.

    Usage::

        {% list_locations as [varname] [options] %}

    Be sure the [varname] has a specific name like ``locations_sidebar`` or
    ``locations_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Approved**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_locations as locations_list limit=5 tags="cool" %}
        {% for location in locations_list %}
            {{ location.location_name }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListLocationNode(context_var, *args, **kwargs)
