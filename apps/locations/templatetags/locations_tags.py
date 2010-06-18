from django.template import Library

register = Library()

@register.inclusion_tag("locations/options.html", takes_context=True)
def location_options(context, user, location):
    context.update({
        "location": location,
        "user": user
    })
    return context

@register.inclusion_tag("locations/nav.html", takes_context=True)
def location_nav(context, user):
    context.update({
        "user": user
    })
    return context

@register.inclusion_tag("locations/search-form.html", takes_context=True)
def location_search(context):
    return context