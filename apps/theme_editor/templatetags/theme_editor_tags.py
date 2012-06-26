from django.template import Library

register = Library()

@register.inclusion_tag("theme_editor/folder_structure.html", takes_context=True)
def folder_structure(context, value):
    context.update({
        "value": value,
    })
    return context
