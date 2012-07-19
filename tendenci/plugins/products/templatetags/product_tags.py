from django.template import Node, Library, TemplateSyntaxError, Variable

from products.models import Product
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


class ListProductsNode(ListNode):
    model = Product
    perms = 'products.view_product'


@register.inclusion_tag("products/search-form.html", takes_context=True)
def product_search(context):
    return context

@register.tag
def list_products(parser, token):
    """
    Used to pull a list of :model:`products.Product` items.

    Usage::

        {% list_products as [varname] [options] %}

    Be sure the [varname] has a specific name like ``products_sidebar`` or 
    ``products_list``. Options can be used as [option]=[value]. Wrap text values
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

        {% list_products as products_list limit=5 tags="cool" %}
        {% for product in products_list %}
            {{ product.name }}
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

    return ListProductsNode(context_var, *args, **kwargs)
