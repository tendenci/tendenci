# -*- coding: utf-8 -*-
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.forms.widgets import DateInput


class RangeWidget(forms.MultiWidget):
    """
    Render 2 inputs with vDatepicker class in order to select a date range.
    """
    template_name = 'model_report/widgets/range_widget.html'

    def __init__(self, widget, *args, **kwargs):
        widgets = (widget, widget)
        kwargs['attrs'] = {'class': 'vDatepicker'}
        super(RangeWidget, self).__init__(widgets=widgets, *args, **kwargs)

    def decompress(self, value):
        return value

    def get_context(self, name, value, attrs):
        context = super(RangeWidget, self).get_context(name, value, attrs)
        widgets = context['widget']['subwidgets']
        context['min'] = DateInput(widgets[0]['attrs']).render(widgets[0]['name'], widgets[0]['value'] or '')
        context['max'] = DateInput(widgets[1]['attrs']).render(widgets[1]['name'], widgets[1]['value'] or '')
        return context


class RangeField(forms.MultiValueField):
    """
    Field to filter date values by range.
    """
    default_error_messages = {
        'invalid_start': _(u'Enter a valid start value.'),
        'invalid_end': _(u'Enter a valid end value.'),
    }

    def __init__(self, field_class, widget=forms.TextInput, *args, **kwargs):
        if 'initial' not in kwargs:
            kwargs['initial'] = ['', '']

        fields = (field_class(), field_class())

        super(RangeField, self).__init__(
                fields=fields,
                widget=RangeWidget(widget),
                *args, **kwargs
                )
        self.label = force_text(field_class().label)


    def compress(self, data_list):
        if data_list:
            return [self.fields[0].clean(data_list[0]), self.fields[1].clean(data_list[1])]
        return None
