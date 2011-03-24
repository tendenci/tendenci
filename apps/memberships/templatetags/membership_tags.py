from django.template import Library

register = Library()

@register.inclusion_tag("memberships/options.html", takes_context=True)
def membership_options(context, user, membership):
    context.update({
        "opt_object": membership,
        "user": user
    })
    return context

@register.inclusion_tag("memberships/nav.html", takes_context=True)
def membership_nav(context, user, membership=None):
    context.update({
        "nav_object" : membership,
        "user": user
    })
    return context

@register.inclusion_tag("memberships/search-form.html", takes_context=True)
def membership_search(context):
    return context

@register.inclusion_tag("memberships/entries/options.html", takes_context=True)
def entry_options(context, user, entry):
    context.update({
        "opt_object": entry,
        "user": user
    })
    return context

@register.inclusion_tag("memberships/entries/nav.html", takes_context=True)
def entry_nav(context, user, entry=None):
    context.update({
        "nav_object" : entry,
        "user": user
    })
    return context

@register.inclusion_tag("memberships/entries/search-form.html", takes_context=True)
def entry_search(context):
    return context

@register.inclusion_tag('memberships/renew-button.html', takes_context=True)
def renew_button(context):
    return context
