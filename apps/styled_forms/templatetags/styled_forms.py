from django.template import Context
from django.template.loader import get_template
from django import template

register = template.Library()

@register.filter
def is_checkbox(field):
    return field.field.widget.__class__.__name__.lower() == "checkboxinput"

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