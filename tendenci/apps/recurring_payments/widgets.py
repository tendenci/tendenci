import datetime
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from tendenci.addons.recurring_payments.models import BILLING_PERIOD_CHOICES, DUE_SORE_CHOICES

class BillingDateSelectInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        return mark_safe('%s day(s) after billing cycle end date' \
                         % super(BillingDateSelectInput, self).render(name, value, attrs))

class BillingDateSelectWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        self.attrs = attrs
        self.pos_d = {'num_days': (0, forms.TextInput()),
                      'due_sore':(1, forms.Select()),
                       }
        self.widgets = ()
        if self.pos_d:
            items = self.pos_d.values()
            items.sort()
            self.widgets = [item[1] for item in items]

        super(BillingDateSelectWidget, self).__init__(self.widgets, attrs)

    def render(self, name, value, attrs=None):
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)

        # num_days
        num_days_widget = self.pos_d['num_days'][1]
        num_days_widget.attrs = {'size':'8'}
        rendered_num_days = self.render_widget(num_days_widget, name, value, final_attrs,
                                             self.pos_d['num_days'][0], id_)

        # billing cycle start or end dt
        due_sore_widget = self.pos_d['due_sore'][1]
        due_sore_widget.choices = DUE_SORE_CHOICES
        rendered_due_sore = self.render_widget(due_sore_widget,
                                    name, value, final_attrs, self.pos_d['due_sore'][0], id_)

        output_html = """
                        <div id="billing_dt_select">
                            %s day(s) after billing cycle %s date
                        </div>
                      """ % (rendered_num_days,
                             rendered_due_sore
                             )

        return mark_safe(output_html)



    def render_widget(self, widget, name, value, attrs, index=0, id=None):
        i = index
        id_ = id
        if value:
            try:
                widget_value = value[i]
            except IndexError:
                self.fields['billing_dt_select'].initial = None
        else:
            widget_value = None
        if id_:
            final_attrs = dict(attrs, id='%s_%s' % (id_, i))

        return widget.render(name+'_%s' %i, widget_value, final_attrs)


    def decompress(self, value):
        if value:
            return value.split(",")
        return None


class BillingCycleWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        self.attrs = attrs
        self.pos_d = {'billing_frequency': (0, forms.TextInput()),
                      'billing_period': (1, forms.Select()),
                       }
        self.widgets = ()
        if self.pos_d:
            items = self.pos_d.values()
            items.sort()
            self.widgets = [item[1] for item in items]

        super(BillingCycleWidget, self).__init__(self.widgets, attrs)

    def render(self, name, value, attrs=None):
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)

        # billing_frequency
        billing_frequency_widget = self.pos_d['billing_frequency'][1]
        billing_frequency_widget.attrs = {'size':'8'}
        rendered_billing_frequency = self.render_widget(billing_frequency_widget, name, value, final_attrs,
                                             self.pos_d['billing_frequency'][0], id_)

        # billing_period
        billing_period_widget = self.pos_d['billing_period'][1]
        billing_period_widget.choices = BILLING_PERIOD_CHOICES
        rendered_billing_period = self.render_widget(billing_period_widget,
                                    name, value, final_attrs, self.pos_d['billing_period'][0], id_)


        output_html = """
                        <div id="billing_cycle">
                            Every %s %s
                        </div>
                      """ % (rendered_billing_frequency,
                             rendered_billing_period
                             )

        return mark_safe(output_html)



    def render_widget(self, widget, name, value, attrs, index=0, id=None):
        i = index
        id_ = id
        if value:
            try:
                widget_value = value[i]
            except IndexError:
                self.fields['billing_cycle'].initial = None
        else:
            widget_value = None
        if id_:
            final_attrs = dict(attrs, id='%s_%s' % (id_, i))

        return widget.render(name+'_%s' %i, widget_value, final_attrs)


    def decompress(self, value):
        if value:
            return value.split(",")
        return None
