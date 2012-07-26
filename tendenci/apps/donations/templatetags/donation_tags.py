from django.template import Library

register = Library()

@register.inclusion_tag("donations/nav.html", takes_context=True)
def donation_nav(context, user, donation=None):
    context.update({
        'nav_object': donation,
        "user": user
    })
    return context

@register.inclusion_tag("donations/search-form.html", takes_context=True)
def donation_search(context):
    return context