from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from widgets import (TypeExpMethodWidget, NoticeTimeTypeWidget,
                     AppFieldSelectionWidget)
from tendenci.apps.site_settings.utils import get_setting


class TypeExpMethodField(forms.MultiValueField):
    def __init__(self, required=True, widget=TypeExpMethodWidget(attrs=None, fields_pos_d=None),
                label=None, initial=None, help_text=None):
        myfields = ()
        super(TypeExpMethodField, self).__init__(myfields, required, widget,
                                          label, initial, help_text)

    def clean(self, value):
        return self.compress(value)

    def compress(self, data_list):
        for i in range(0, len(data_list)):
            if type(data_list[i]) is bool:
                if data_list[i] == False:
                    data_list[i] = ''
                else:
                    data_list[i] = '1'
            if data_list[i] == None:
                data_list[i] = ''

        if data_list:
            return ','.join(data_list)
        return None


class NoticeTimeTypeField(forms.MultiValueField):
    def __init__(self, required=True, widget=NoticeTimeTypeWidget(attrs=None),
                label=None, initial=None, help_text=None):
        myfields = ()
        super(NoticeTimeTypeField, self).__init__(myfields, required, widget,
                                          label, initial, help_text)

    def clean(self, value):
        return self.compress(value)

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None


class PriceInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        currency_symbol = get_setting('site', 'global', 'currencysymbol')
        if currency_symbol == u'':
            currency_symbol = '$'
        return mark_safe('$ %s' % super(PriceInput, self).render(name, value, attrs))


class AppFieldSelectionField(forms.MultipleChoiceField):
    widget = AppFieldSelectionWidget

    def __init__(self, *args, **kwargs):
        # dynamic build choices
        all_fields_tuple = self.widget.all_fields_tuple
        all_fields_dict = self.widget.all_fields_dict
        kwargs['choices'] = []

        for field_name in all_fields_tuple:
            if field_name in all_fields_dict:
                label = all_fields_dict[field_name].verbose_name
                if not label:
                    label = all_fields_dict[field_name].name
            else:
                label = field_name
            kwargs['choices'].append((field_name, label))

        super(AppFieldSelectionField, self).__init__(*args, **kwargs)


class MembershipTypeModelChoiceField(forms.ModelChoiceField):
    customer = None
    corp_membership = None

    def label_from_instance(self, obj):
        return obj.get_price_display(self.customer, self.corp_membership)
