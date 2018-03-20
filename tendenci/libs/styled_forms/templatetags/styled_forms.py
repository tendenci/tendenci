from django.template.loader import get_template
from django import template

register = template.Library()

@register.filter
def is_header(field):
    return field.field.widget.__class__.__name__.lower() == "header"

@register.filter
def is_description(field):
    return field.field.widget.__class__.__name__.lower() == "description"

@register.filter
def is_horizontal_rule(field):
    return field.field.widget.__class__.__name__.lower() == "horizontal_rule"

@register.filter
def is_checkbox(field):
    return field.field.widget.__class__.__name__.lower() == "checkboxinput"

@register.filter
def is_radioselect(field):
    return field.field.widget.__class__.__name__.lower() == "radioselect"

@register.filter
def is_checkboxselectmultiple(field):
    return field.field.widget.__class__.__name__.lower() == "checkboxselectmultiple"

@register.filter
def is_textinput(field):
    return field.field.widget.__class__.__name__.lower() == "textinput"

@register.filter
def is_fileinput(field):
    return "fileinput" in field.field.widget.__class__.__name__.lower()

@register.filter
def col_sm_width(field):
    """
    Get the width for the field column specified in the class "col-sm-x".
    The width is calculated based on the size of the field.
    """
    f = field.field
    if field.name == 'salutation':
        return 5
    if hasattr(f, 'widget') and 'size' in f.widget.attrs:
        try:
            size = int(f.widget.attrs['size'])
            if size >= 30:
                return 8
            if size >= 25:
                return 7
            if size >= 20:
                return 6
            if size >= 10:
                return 5
            if size >= 6:
                return 4
            if size <= 5:
                return 3
        except:
            pass
    return 8

@register.filter
def styled_form(form):
    template = get_template('styled_forms/form.html')
    return template.render(context={'form':form})

@register.filter
def styled_multi_forms(forms):
    template = get_template('styled_forms/multi_form.html')
    return template.render(context={'forms':forms})

@register.filter
def styled_form_set(form_set):
    template = get_template('styled_forms/form_set.html')
    return template.render(context={'form_set':form_set})

@register.filter
def styled_dynamic_form_set(form_set):
    template = get_template('styled_forms/dynamic_form_set.html')
    return template.render(context={'form_set':form_set})
