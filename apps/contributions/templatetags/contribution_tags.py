from django.template import Library

register = Library()

@register.inclusion_tag("contributions/options.html", takes_context=True)
def contribution_options(context, user, contribution):
    context.update({
        "contribution": contribution,
        "user": user
    })
    return context

@register.inclusion_tag("contributions/nav.html", takes_context=True)
def contribution_nav(context, user):
    context.update({
        "user": user
    })
    return context

@register.inclusion_tag("contributions/search-form.html", takes_context=True)
def contribution_search(context):
    return context