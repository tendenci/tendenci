from django.template import Library

register = Library()

@register.inclusion_tag("entities/options.html", takes_context=True)
def entity_options(context, user, entity):
    context.update({
        "opt_object": entity,
        "user": user
    })
    return context

@register.inclusion_tag("entities/nav.html", takes_context=True)
def entity_nav(context, user, entity=None):
    context.update({
        "nav_object": entity,
        "user": user
    })
    return context


@register.inclusion_tag("entities/search-form.html", takes_context=True)
def entity_search(context):
    return context