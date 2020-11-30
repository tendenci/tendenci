from django.template import Library, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.directories.models import Directory


register = Library()


@register.inclusion_tag("directories/options.html", takes_context=True)
def directory_options(context, user, directory):
    context.update({
        "opt_object": directory,
        "user": user,
        "is_member_of_directory": directory.has_membership_with(user)
    })
    return context


@register.inclusion_tag("directories/nav.html", takes_context=True)
def directory_nav(context, user, directory=None):
    context.update({
        "nav_object" : directory,
        "user": user
    })
    return context


@register.inclusion_tag("directories/search-form.html", takes_context=True)
def directory_search(context):
    return context


@register.inclusion_tag("directories/top_nav_items.html", takes_context=True)
def directory_current_app(context, user, directory=None):
    context.update({
        "app_object" : directory,
        "user": user
    })
    return context


@register.inclusion_tag("directories/pricing-nav.html", takes_context=True)
def directory_pricing_nav(context, user, directory_pricing=None):
    context.update({
        'nav_object': directory_pricing,
        "user": user
    })
    return context


@register.inclusion_tag("directories/pricing-options.html", takes_context=True)
def directory_pricing_options(context, user, directory_pricing):
    context.update({
        "opt_object": directory_pricing,
        "user": user
    })
    return context


@register.inclusion_tag("directories/pricing-table.html", takes_context=True)
def directory_pricing_table(context):
    from tendenci.apps.directories.models import DirectoryPricing
    directory_pricings =DirectoryPricing.objects.filter(status=True).order_by('duration')
    show_premium_price = False
    premium_jp = DirectoryPricing.objects.filter(status=True).filter(premium_price__gt=0)
    if premium_jp:
        show_premium_price = True
    context.update({
        "directory_pricings": directory_pricings,
        'show_premium_price': show_premium_price
    })
    return context


@register.inclusion_tag("directories/top_nav_items_pricing.html", takes_context=True)
def directory_pricing_current_app(context, user, directory_pricing=None):
    context.update({
        'app_object': directory_pricing,
        "user": user
    })
    return context


class ListDirectoriesNode(ListNode):
    model = Directory
    perms = 'directories.view_directory'


@register.tag
def list_directories(parser, token):
    """
    Used to pull a list of :model:`directories.Directory` items.

    Usage::

        {% list_directories as [varname] [options] %}

    Be sure the [varname] has a specific name like ``directories_sidebar`` or
    ``directories_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Headline A-Z**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_directories as directories_list limit=5 tags="cool" %}
        {% for directory in directories_list %}
            {{ directory.headline }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = 'headline'

    return ListDirectoriesNode(context_var, *args, **kwargs)
