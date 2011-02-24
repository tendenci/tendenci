from datetime import datetime

from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
from pages.models import Page

register = Library()


@register.inclusion_tag("pages/options.html", takes_context=True)
def page_options(context, user, page):
    context.update({
        "opt_object": page,
        "user": user
    })
    return context


@register.inclusion_tag("pages/nav.html", takes_context=True)
def page_nav(context, user, page=None):
    context.update({
        'nav_object': page,
        "user": user
    })
    return context


@register.inclusion_tag("pages/search-form.html", takes_context=True)
def page_search(context):
    return context


class ListPageNode(ListNode):
    model = Page


@register.tag
def list_pages(parser, token):
    """
    Example:

    {% list_pages as pages user=user limit=3 %}
    {% for page in pages %}
        {{ page.title }}
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

    return ListPageNode(context_var, *args, **kwargs)
