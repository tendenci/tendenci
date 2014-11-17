from django.template import Library

register = Library()


@register.inclusion_tag("redirects/options.html", takes_context=True)
def redirect_options(context, user, redirect):
    context.update({
        "opt_object": redirect,
        "user": user
    })
    return context


@register.inclusion_tag("redirects/nav.html", takes_context=True)
def redirect_nav(context, user, redirect=None):
    context.update({
        "nav_object" : redirect,
        "user": user
    })
    return context


@register.inclusion_tag("redirects/top_nav_items.html", takes_context=True)
def redirect_current_app(context, user, redirect=None):
    context.update({
        "app_object" : redirect,
        "user": user
    })
    return context


@register.inclusion_tag("redirects/search-form.html", takes_context=True)
def redirect_search(context):
    return context
