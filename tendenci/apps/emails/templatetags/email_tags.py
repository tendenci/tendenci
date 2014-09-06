from django.template import Library

register = Library()

@register.inclusion_tag("emails/options.html", takes_context=True)
def emails_options(context, email):
    context.update({
        "opt_object": email,
    })
    return context

@register.inclusion_tag("emails/nav.html", takes_context=True)
def emails_nav(context, email=None):
    context.update({
        "nav_object": email,
    })
    return context