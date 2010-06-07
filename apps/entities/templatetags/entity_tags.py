from django.template import Library

register = Library()

@register.inclusion_tag("entities/options.html", takes_context=True)
def entity_options(context, user, entity):
    context.update({
        "entity": entity,
        "user": user
    })
    return context

@register.inclusion_tag("entities/nav.html", takes_context=True)
def entity_nav(context, user):
    context.update({
        "user": user
    })
    return context