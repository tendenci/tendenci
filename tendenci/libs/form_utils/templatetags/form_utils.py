# -*- coding: utf-8 -*-
"""
templatetags for django-form-utils

"""
from __future__ import unicode_literals

from django import forms
from django import template
from django.template.loader import render_to_string
from django.utils import six

from ..forms import BetterForm, BetterModelForm
from ..utils import select_template_from_string

register = template.Library()


@register.filter
def render(form, template_name=None):
    """
    Renders a ``django.forms.Form`` or
    ``form_utils.forms.BetterForm`` instance using a template.

    The template name(s) may be passed in as the argument to the
    filter (use commas to separate multiple template names for
    template selection).

    If not provided, the default template name is
    ``form_utils/form.html``.

    If the form object to be rendered is an instance of
    ``form_utils.forms.BetterForm`` or
    ``form_utils.forms.BetterModelForm``, the template
    ``form_utils/better_form.html`` will be used instead if present.

    """
    default = 'form_utils/form.html'
    if isinstance(form, (BetterForm, BetterModelForm)):
        default = ','.join(['form_utils/better_form.html', default])
    tpl = select_template_from_string(template_name or default)

    return tpl.render(template.Context({'form': form}))


@register.filter
def label(boundfield, contents=None):
    """Render label tag for a boundfield, optionally with given contents."""
    label_text = contents or boundfield.label
    id_ = boundfield.field.widget.attrs.get('id') or boundfield.auto_id

    return render_to_string("forms/_label.html", {
        "label_text": label_text,
        "id": id_,
        "field": boundfield})


@register.filter
def value_text(boundfield):
    """Return the value for given boundfield as human-readable text."""
    val = boundfield.value()
    # If choices is set, use the display label
    return six.text_type(
        dict(getattr(boundfield.field, "choices", [])).get(val, val))


@register.filter
def selected_values(boundfield):
    """Return the values for given multiple-select as human-readable text."""
    val = boundfield.value()
    # If choices is set, use the display label
    choice_dict = dict(getattr(boundfield.field, "choices", []))
    return [six.text_type(choice_dict.get(v, v)) for v in val]


@register.filter
def optional(boundfield):
    """Return True if given boundfield is optional, else False."""
    return not boundfield.field.required


@register.filter
def is_checkbox(boundfield):
    """Return True if this field's widget is a CheckboxInput."""
    return isinstance(boundfield.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple(boundfield):
    """Return True if this field is a MultipleChoiceField."""
    return isinstance(boundfield.field, forms.MultipleChoiceField)


@register.filter
def is_select(boundfield):
    """Return True if this field is a ChoiceField (or subclass)."""
    return isinstance(boundfield.field, forms.ChoiceField)


@register.filter
def is_radio(boundfield):
    """
    Return True if this field's widget's class name contains 'radio'.

    This hacky approach is necessary in order to support django-floppyforms,
    whose RadioSelect does not inherit from Django's built-in RadioSelect.

    """
    return 'radio' in boundfield.field.widget.__class__.__name__.lower()
