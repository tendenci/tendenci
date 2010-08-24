from django.template import Library

register = Library()

@register.inclusion_tag("help_files/options.html", takes_context=True)
def help_file_options(context, user, help_file):
    context.update({
        "opt_object": help_file,
        "user": user
    })
    return context

@register.inclusion_tag("help_files/nav.html", takes_context=True)
def help_file_nav(context, user, help_file=None):
    context.update({
        "nav_object" : help_file,
        "user": user
    })
    return context

@register.inclusion_tag("help_files/search-form.html", takes_context=True)
def help_file_search(context):
    return context