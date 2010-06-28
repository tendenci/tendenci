from django.template import Library

register = Library()

@register.inclusion_tag("locations/options.html", takes_context=True)
def location_options(context, user, location):
    context.update({
        "opt_object": location,
        "user": user
    })
    return context

@register.inclusion_tag("locations/nav.html", takes_context=True)
def location_nav(context, user, location=None):
    context.update({
        "nav_object": location,
        "user": user
    })
    return context

@register.inclusion_tag("locations/search-form.html", takes_context=True)
def location_search(context):
    return context