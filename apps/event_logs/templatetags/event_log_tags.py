from django.template import Library

register = Library()

@register.inclusion_tag("event_logs/options.html", takes_context=True)
def event_log_options(context, user, event_log):
    context.update({
        "event_log": event_log,
        "user": user
    })
    return context

@register.inclusion_tag("event_logs/nav.html", takes_context=True)
def event_log_nav(context, user):
    context.update({
        "user": user
    })
    return context

@register.inclusion_tag("event_logs/search-form.html", takes_context=True)
def event_log_search(context):
    return context