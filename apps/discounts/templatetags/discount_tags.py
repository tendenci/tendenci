from django.template import Library, TemplateSyntaxError, Variable

from base.template_tags import ListNode, parse_tag_kwargs
from discounts.models import Discount

register = Library()

@register.inclusion_tag("discounts/options.html", takes_context=True)
def discount_options(context, user, discount):
    context.update({
        "opt_object": discount,
        "user": user
    })
    return context

@register.inclusion_tag("discounts/nav.html", takes_context=True)
def discount_nav(context, user, discount=None):
    context.update({
        "nav_object": discount,
        "user": user
    })
    return context

@register.inclusion_tag("discounts/search-form.html", takes_context=True)
def discount_search(context):
    return context
