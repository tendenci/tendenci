from django.template import Library

register = Library()

@register.inclusion_tag("events/options.html", takes_context=True)
def event_options(context, user, event):
    context.update({
        "opt_object": event,
        "user": user
    })
    return context

@register.inclusion_tag("events/nav.html", takes_context=True)
def event_nav(context, user, event=None):
    context.update({
        "nav_object" : event,
        "user": user
    })
    return context

@register.inclusion_tag("events/search-form.html", takes_context=True)
def event_search(context):
    return context