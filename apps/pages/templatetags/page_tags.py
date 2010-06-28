from django.template import Library

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