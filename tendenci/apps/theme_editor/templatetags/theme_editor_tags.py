from django.template import Library

register = Library()

@register.inclusion_tag("theme_editor/folder_structure.html", takes_context=True)
def folder_structure(context, value):
    context.update({
        "value": value,
    })
    return context

@register.inclusion_tag("theme_editor/details.html", takes_context=True)
def theme_detail(context, theme, current_theme):
    context.update({
        "theme": theme,
        "current_theme": current_theme,
    })
    return context
