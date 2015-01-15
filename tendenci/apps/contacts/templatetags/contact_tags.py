from django.template import Library


register = Library()


@register.inclusion_tag("contacts/options.html", takes_context=True)
def contact_options(context, user, contact):
    context.update({
        "opt_object": contact,
        "user": user
    })
    return context


@register.inclusion_tag("contacts/nav.html", takes_context=True)
def contact_nav(context, user, contact=None):
    context.update({
        "nav_object" : contact,
        "user": user
    })
    return context


@register.inclusion_tag("contacts/search-form.html", takes_context=True)
def contact_search(context):
    return context


@register.inclusion_tag("contacts/top_nav_items.html", takes_context=True)
def contact_current_app(context, user, contact=None):
    context.update({
        "app_object": contact,
        "user": user
    })
    return context
