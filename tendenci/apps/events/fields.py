from __future__ import absolute_import
from collections import OrderedDict
from datetime import datetime, timedelta

from django.forms import ChoiceField, MultiValueField
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

from tendenci.apps.base.widgets import SplitDateTimeWidget
from .widgets import UseCustomRegWidget


class Reg8nDtWidget(Widget):

    reg8n_dict = {
        'start_dt': '',
        'end_dt': '',
    }

    def render(self, name, value, attrs=None, choices=()):
        str_format_kwargs = []
        for k, v in self.reg8n_dict.items():
            # date field
            str_format_kwargs.append(SplitDateTimeWidget().render(
                '%s' % (k),  # name
                self.reg8n_dict.get(k),  # value
                {
                    'id': '%s' % (k)
                }  # id attribute
            ))

        # string format template
        html = u"<div>%s to %s</div>" % tuple(str_format_kwargs)
        return mark_safe(html)


class Reg8nDtField(ChoiceField):
    """
        Inherits from ChoiceField and sets some default meta data
        note: This field injects 'data' into other form fields and
        causes formsets to consider new instances as 'modified' even
        if a user introduces no changes to the form.
    """
    widget = Reg8nDtWidget

    def __init__(self, *args, **kwargs):
        super(Reg8nDtField, self).__init__(*args, **kwargs)
        self.build_widget_reg8n_dict()

    def build_widget_reg8n_dict(self, *args, **kwargs):
        """
        Build widget reg8n dictionary.
        Pass dictionary to widget.
        Please call() within form-init method
        """
        prefix = '%s-' % kwargs.get('prefix') if kwargs.get('prefix') else ''
        instance = kwargs.get('instance', None)
        initial = kwargs.get('initial') or {}

        today = datetime.today()
        one_hour = timedelta(hours=1)

        if instance:
            reg8n_dict = OrderedDict([
                ('%sstart_dt' % prefix, instance.start_dt),
                ('%send_dt' % prefix, instance.end_dt),
            ])
        else:
            reg8n_dict = OrderedDict([
                ('%sstart_dt' % prefix, initial.get('start_dt') or (today)),  # 2 hrs
                ('%send_dt' % prefix, initial.get('end_dt') or (today+(one_hour*3))),  # 3 hrs
            ])

        self.widget.reg8n_dict = reg8n_dict
        return reg8n_dict


class UseCustomRegField(MultiValueField):
    def __init__(
        self,
        required=True,
        widget=UseCustomRegWidget(attrs=None),
        label=None,
        initial=None,
        help_text=None
    ):
        myfields = ()
        super(UseCustomRegField, self).__init__(
            myfields, required, widget, label, initial, help_text)

    def clean(self, value):
        return self.compress(value)

    def compress(self, data_list):
        for i, item in enumerate(data_list):
            if type(item) is bool:
                if item is False:
                    data_list[i] = u'0'
                else:
                    data_list[i] = u'1'
            if item is None:
                data_list[i] = u''

        if data_list:
            return ','.join(data_list)
        return None
