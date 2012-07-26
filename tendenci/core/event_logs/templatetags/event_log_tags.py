from django.template import Library

register = Library()


@register.inclusion_tag("event_logs/options.html", takes_context=True)
def event_log_options(context, user, event_log):
    context.update({
        "opt_object": event_log,
        "user": user
    })
    return context


@register.inclusion_tag("event_logs/nav.html", takes_context=True)
def event_log_nav(context, user, event_log=None):
    context.update({
        "nav_object": event_log,
        "user": user
    })
    return context


@register.inclusion_tag("event_logs/search-form.html", takes_context=True)
def event_log_search(context, search_form):
    context.update({
        "search_form": search_form,
    })
    return context
