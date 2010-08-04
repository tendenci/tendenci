from django.template import Library

register = Library()

@register.inclusion_tag("directories/options.html", takes_context=True)
def directory_options(context, user, directory):
    context.update({
        "opt_object": directory,
        "user": user
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