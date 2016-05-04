# -*- coding: utf-8 -*-
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode


class RangeWidget(forms.MultiWidget):
    """
    Render 2 inputs with vDatepicker class in order to select a date range.
    """
    def __init__(self, widget, *args, **kwargs):
        widgets = (widget, widget)
        kwargs['attrs'] = {'class': 'vDatepicker'}
        super(RangeWidget, self).__init__(widgets=widgets, *args, **kwargs)

    def decompress(self, value):
        return value

    def format_output(self, rendered_widgets):
        widget_context = {'min': rendered_widgets[0], 'max': rendered_widgets[1]}
        return render_to_string('model_report/widgets/range_widget.html', widget_context)


class RangeField(forms.MultiValueField):
    """
    Field to filter date values by range.
    """
    default_error_messages = {
        'invalid_start': _(u'Enter a valid start value.'),
        'invalid_end': _(u'Enter a valid end value.'),
    }

    def __init__(self, field_class, widget=forms.TextInput, *args, **kwargs):
        if not 'initial' in kwargs:
            kwargs['initial'] = ['', '']

        fields = (field_class(), field_class())

        super(RangeField, self).__init__(
                fields=fields,
                widget=RangeWidget(widget),
                *args, **kwargs
                )
        self.label = force_unicode(field_class().label)

    def compress(self, data_list):
        if data_list:
            return [self.fields[0].clean(data_list[0]), self.fields[1].clean(data_list[1])]
        return None
