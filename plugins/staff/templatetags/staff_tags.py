from django.template import Library

register = Library()

@register.inclusion_tag("staff/options.html", takes_context=True)
def staff_options(context, user, staff):
    context.update({
        "opt_object": staff,
        "user": user
    })
    return context

@register.inclusion_tag("staff/search-form.html", takes_context=True)
def staff_search(context):
    return context