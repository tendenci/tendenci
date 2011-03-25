from datetime import datetime, timedelta
from django.http import QueryDict
from django.forms import ChoiceField
from django.forms.widgets import Widget, TextInput
from django.utils.safestring import mark_safe
from django.template.defaultfilters import date as date_filter
from base.widgets import SplitDateTimeWidget


class Reg8nDtWidget(Widget):

    reg8n_dict = {}

    def render(self, name, value, attrs=None, choices=()):

        # rip prefix from name
        name_prefix = name.split('-')[0]
        id_prefix = 'id_%s' % name_prefix

        str_format_kwargs = {}
        for k, v in self.reg8n_dict.items():

            if k.split('_')[1] == 'price':
                # text field
                str_format_kwargs[k] = TextInput().render(
                    '%s-%s' % (name_prefix, k),  # name
                    self.reg8n_dict.get(k),  # value
                    {'id': '%s-%s' % (id_prefix, k)}  # id attribute
                )

            elif k.split('_')[1] == 'dt':
                # date field
                str_format_kwargs[k] = SplitDateTimeWidget().render(
                    '%s-%s' % (name_prefix, k),  # name
                    self.reg8n_dict.get(k),  # value
                    {'id': '%s-%s' % (id_prefix, k)}  # id attribute
                )

        # string format template
        html  = u"""
            <div>%(early_price)s after %(early_dt)s</div>
            <div>%(regular_price)s after %(regular_dt)s</div>
            <div>%(late_price)s after %(late_dt)s</div>
            <div>registration ends %(end_dt)s</div>
            """ % str_format_kwargs

        return mark_safe(html)


class Reg8nDtField(ChoiceField): 
    """
        Inherits from MultipleChoiceField and
        sets some default meta data
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
        instance = kwargs.get('instance')
        prefix = kwargs.get('prefix')
        query_dict = {}

        if args and args[0]:
            query_dict = args[0]

        reg8n_dict = {
            'early_price': 0,
            'regular_price': 0,
            'late_price': 0,
            'early_dt': datetime.today(),
            'regular_dt': datetime.today() + timedelta(days=1),
            'late_dt': datetime.today() + timedelta(days=2),
            'end_dt': datetime.today() + timedelta(days=3),
        }

        # save ourselves from looping; no need
        if not query_dict and not instance:
            self.widget.reg8n_dict = reg8n_dict
            return reg8n_dict

        for k, v in reg8n_dict.items():
            if query_dict:  # edit page with querystring

                if k.split('_')[1] == 'price':
                    reg8n_dict[k] = query_dict.get('%s-%s' % (prefix, k))
                elif k.split('_')[1] == 'dt':
                    str_date = query_dict.get('%s-%s_0' % (prefix, k))
                    str_time = query_dict.get('%s-%s_1' % (prefix, k))

                    try:
                        reg8n_dict[k] = datetime.strptime('%s %s' % (str_date, str_time), '%Y-%m-%d %I:%M %p')
                    except ValueError:   # if incorrect dt format is passed
                        reg8n_dict[k] = u''

            elif instance and hasattr(instance, k):  # edit page without querystring
                    reg8n_dict[k] = getattr(instance, k)

        self.widget.reg8n_dict = reg8n_dict
        return reg8n_dict