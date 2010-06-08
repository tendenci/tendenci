from django.template import Library

register = Library()

@register.inclusion_tag("pages/options.html", takes_context=True)
def page_options(context, user, page):
    context.update({
        "page": page,
        "user": user
    })
    return context

@register.inclusion_tag("pages/nav.html", takes_context=True)
def page_nav(context, user):
    context.update({
        "user": user
    })
    return context

@register.inclusion_tag("pages/search-form.html", takes_context=True)
def page_search(context):
    return context