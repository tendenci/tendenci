from django.template import Library

register = Library()

@register.inclusion_tag("files/options.html", takes_context=True)
def file_options(context, user, file):
    context.update({
        "file": file,
        "user": user
    })
    return context

@register.inclusion_tag("files/nav.html", takes_context=True)
def file_nav(context, user):
    context.update({
        "user": user
    })
    return context

@register.inclusion_tag("files/search-form.html", takes_context=True)
def file_search(context):
    return context