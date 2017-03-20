from django.template import Library


register = Library()


@register.inclusion_tag("emails/options.html", takes_context=True)
def emails_options(context, email):
    context.update({
        "opt_object" : email,
    })
    return context


@register.inclusion_tag("emails/nav.html", takes_context=True)
def emails_nav(context, user, email=None):
    context.update({
        "nav_object" : email,
        "user" : user,
    })
    return context


@register.inclusion_tag("emails/top_nav_items.html", takes_context=True)
def emails_current_app(context, email=None):
    context.update({
        "app_object" : email,
    })
    return context
