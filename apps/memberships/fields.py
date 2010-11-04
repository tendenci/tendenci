from django import forms
from django.utils.safestring import mark_safe

from site_settings.utils import get_setting

PERIOD_UNIT_CHOICE = (
                      ("days", "Days"),
                      ("months", "Months"),
                      ("years", "Years"),)


class PeriodWidget(forms.MultiWidget):
    """
        Period widget
    """
    def __init__(self, attrs=None):
        self.attrs = attrs
        widgets = (
                     forms.TextInput(attrs={'size':'5'}),
                     forms.Select(choices=PERIOD_UNIT_CHOICE),
                     )
        super(PeriodWidget, self).__init__(widgets, attrs)
    
    def decompress(self, value):
        if value:
            return value.split(",")
        return [None, None]
    
    def render(self, name, value, attrs=None):
        return super(PeriodWidget, self).render(name, value, attrs)

    
    
class PeriodField(forms.MultiValueField):
    """
        A field contains:
            period
            period_unit
    """
    def __init__(self, required=True, widget=PeriodWidget(attrs=None),
                label=None, initial=None, help_text=None):
        myfields = (
                    forms.CharField(max_length=10, label="Period"), 
                    forms.ChoiceField(choices=PERIOD_UNIT_CHOICE),
                    )
        super(PeriodField, self).__init__(myfields, required, widget,
                                          label, initial, help_text)  

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None
 
class JoinExpMethodWidget(forms.MultiWidget):
    """
        Period widget
    """
    def __init__(self, attrs=None):
        self.attrs = attrs
        join_exp_method_day = forms.TextInput(attrs={'size':'5'})
        JOIN_EXP_METHOD_CHOICE = (
                                  ("0", "End of full period"),
                                  ("1", mark_safe("%s day(s) at signup month" % \
                                join_exp_method_day.render('join_exp_method_day', '1', attrs))),)
        widgets = (
                     forms.RadioSelect(choices=JOIN_EXP_METHOD_CHOICE),
                     #forms.TextInput(attrs={'size':'5'}),
                     )
        super(JoinExpMethodWidget, self).__init__(widgets, attrs)
    
    def decompress(self, value):
        if value:
            return value.split(",")
        return [None, None]
    
    def render(self, name, value, attrs=None):
        return super(JoinExpMethodWidget, self).render(name, value, attrs)   
    
class JoinExpMethodField(forms.MultiValueField):
    """
        A field contains:
            expiration_method
            expiration_method_day
    """
    def __init__(self, required=True, widget=JoinExpMethodWidget(attrs=None),
                label=None, initial=None, help_text=None):
        #expiration_method_day = forms.CharField(max_length=10)
        JOIN_EXP_METHOD_CHOICE = (
                                  ("0", "End of full period"),
                                  ("1", " day(s) at signup month"),)
        myfields = (
                    forms.ChoiceField(label="Expires On", choices=JOIN_EXP_METHOD_CHOICE),
                    forms.CharField(max_length=10), 
                    )
        super(JoinExpMethodField, self).__init__(myfields, required, widget,
                                          label, initial, help_text)  

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None
    
class PriceInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        currency_symbol = get_setting('site', 'global', 'currencysymbol')
        if currency_symbol == '': currency_symbol = "$"
        return mark_safe('$ %s' % super(PriceInput, self).render(name, value, attrs))
        
