from django.template import Context
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
def styled_form(form):
    template = get_template('styled_forms/form.html')
    c = Context({'form':form})
    return template.render(c)

@register.filter
def styled_multi_forms(forms):
    template = get_template('styled_forms/multi_form.html')
    c = Context({'forms':forms})
    return template.render(c)

@register.filter
def styled_form_set(form_set):
    template = get_template('styled_forms/form_set.html')
    c = Context({'form_set':form_set})
    return template.render(c)

@register.filter
def styled_dynamic_form_set(form_set):
    template = get_template('styled_forms/dynamic_form_set.html')
    c = Context({'form_set':form_set})
    return template.render(c)
