from django.template import Library

register = Library()

@register.inclusion_tag("user_groups/options.html", takes_context=True)
def user_group_options(context, user, group):
    context.update({
        "group": group,
        "user": user
    })
    return context

@register.inclusion_tag("user_groups/nav.html", takes_context=True)
def user_group_nav(context, user, group=None):
    context.update({
        "nav_object": group,
        "user": user
    })
    return context

@register.inclusion_tag("user_groups/search-form.html", takes_context=True)
def group_search(context):
    return context
