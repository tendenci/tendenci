from django.template import Library

register = Library()

@register.inclusion_tag("services/options.html", takes_context=True)
def service_options(context, user, service):
    context.update({
        "opt_object": service,
        "user": user
    })
    return context

@register.inclusion_tag("services/nav.html", takes_context=True)
def service_nav(context, user, service=None):
    context.update({
        'nav_object': service,
        "user": user
    })
    return context

@register.inclusion_tag("services/search-form.html", takes_context=True)
def service_search(context):
    return context