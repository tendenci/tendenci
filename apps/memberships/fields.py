import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from site_settings.utils import get_setting

PERIOD_UNIT_CHOICE = (
                      ("days", _("Day(s)")),
                      ("months", _("Month(s)")),
                      ("years", _("Year(s)")),)
PERIOD_CHOICES = (
                  ("fixed", _("Fixed")),
                  ("rolling", _("Rolling")),
                  )
MONTHS_CHOICES = (
                    ('01', 'Jan (01)'),
                    ('02', 'Feb (02)'),
                    ('03', 'Mar (03)'),
                    ('04', 'Apr (04)'),
                    ('05', 'May (05)'),
                    ('06', 'Jun (06)'),
                    ('07', 'Jul (07)'),
                    ('08', 'Aug (08)'),
                    ('09', 'Sep (09)'),
                    ('10', 'Oct (10)'),
                    ('11', 'Nov (11)'),
                    ('12', 'Dec (12)'),
                    )
DAYS_CHOICES = [(day, day) for day in range(1, 32)]

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
    
class TypeExpMethodWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        self.attrs = attrs
        self.pos_d = {'period_type': 0,
                      'period': 1,
                      'period_unit':2,
                      'expiration_method':3,
                      'expiration_method_day':4,
                      'renew_expiration_method':5,
                      'renew_expiration_day':6,
                      'renew_expiration_day2':7,
                      'fixed_expiration_method':8,
                      'fixed_expiration_day':9,
                      'fixed_expiration_month':10,
                      'fixed_expiration_year':11,
                      'fixed_expiration_day2':12,
                      'fixed_expiration_month2':13,
                      'fixed_expiration_rollover':14,
                      'fixed_expiration_rollover_days':15,
                       }
        widgets = (
                     #forms.TextInput(attrs={'size':'5'}),
                     #forms.Select(choices=PERIOD_UNIT_CHOICE),
                     )
        super(TypeExpMethodWidget, self).__init__(widgets, attrs)
    
    def render(self, name, value, attrs=None):
        if not isinstance(value, list):
            value = self.decompress(value)
            
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        
        rendered_period_type = self.render_widget(forms.Select(choices=PERIOD_CHOICES), 
                                                  name, value, final_attrs, self.pos_d['period_type'], id_)
        
        rendered_period = self.render_widget(forms.TextInput(attrs={'size':'8'}), name, value, final_attrs, 
                                             self.pos_d['period'], id_)
        rendered_period_unit = self.render_widget(forms.Select(choices=PERIOD_UNIT_CHOICE), 
                                                  name, value, final_attrs, self.pos_d['period_unit'], id_)
        rendered_expiration_method_day = self.render_widget(forms.TextInput(attrs={'size':'8'}), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['expiration_method_day'], id_)
        JOIN_EXP_METHOD_CHOICE = (
                                  ("0", "End of full period"),
                                  ("1", mark_safe("%s day(s) at signup month" % \
                                                  rendered_expiration_method_day)),)
        rendered_expiration_method = self.render_widget(forms.RadioSelect(choices=JOIN_EXP_METHOD_CHOICE), 
                                                  name, value, final_attrs, 
                                                  self.pos_d['expiration_method'], id_)
        
        rendered_renew_expiration_day = self.render_widget(forms.TextInput(attrs={'size':'8'}), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['renew_expiration_day'], id_)
        rendered_renew_expiration_day2 = self.render_widget(forms.TextInput(attrs={'size':'8'}), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['renew_expiration_day2'], id_)
        RENEW_EXP_METHOD_CHOICE = (
                                  ("0", "End of full period"),
                                  ("1", mark_safe("%s day(s) at signup month" % \
                                                  rendered_renew_expiration_day)),
                                  ("2", mark_safe("%s day(s) at renewal month" % \
                                                  rendered_renew_expiration_day2)),)
        rendered_renew_expiration_method = self.render_widget(forms.RadioSelect(choices=RENEW_EXP_METHOD_CHOICE), 
                                                  name, value, final_attrs, 
                                                  self.pos_d['renew_expiration_method'], id_)
        
        rendered_fixed_expiration_day = self.render_widget(forms.Select(choices=DAYS_CHOICES), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_expiration_day'], id_)
        rendered_fixed_expiration_month = self.render_widget(forms.Select(choices=MONTHS_CHOICES), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_expiration_month'], id_)
        # dynamically generate the year choices for ixed_expiration_year
        fixed_expiration_year = ''
        if value:
            try:
                fixed_expiration_year = int(value[self.pos_d['fixed_expiration_year']])
            except:
                pass
        if not fixed_expiration_year:
            fixed_expiration_year = int(datetime.date.today().year)
        years = [(year, year) for year in range(fixed_expiration_year, fixed_expiration_year+20)]

            
        rendered_fixed_expiration_year = self.render_widget(forms.Select(choices=years), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_expiration_year'], id_)
        rendered_fixed_expiration_day2 = self.render_widget(forms.Select(choices=DAYS_CHOICES), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_expiration_day2'], id_)
        rendered_fixed_expiration_month2 = self.render_widget(forms.Select(choices=MONTHS_CHOICES), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_expiration_month2'], id_)
        FIXED_EXP_METHOD_CHOICE = (
                                  ("0", mark_safe("%s %s %s" % (rendered_fixed_expiration_month,
                                                      rendered_fixed_expiration_day,
                                                      rendered_fixed_expiration_year))),
                                  ("1", mark_safe("%s %s of current year" % \
                                                  (rendered_fixed_expiration_month2,
                                                   rendered_fixed_expiration_day2))))
                                
        rendered_fixed_expiration_method = self.render_widget(forms.RadioSelect(choices=FIXED_EXP_METHOD_CHOICE), 
                                                  name, value, final_attrs, 
                                                  self.pos_d['fixed_expiration_method'], id_)
        rendered_fixed_expiration_rollover_days = self.render_widget(forms.TextInput(attrs={'size':'8'}), 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_expiration_rollover_days'], id_)

        rendered_fixed_expiration_rollover = self.render_widget(forms.CheckboxInput(),
                                                       name, value, final_attrs, 
                                                       self.pos_d['fixed_expiration_rollover'], id_)
        
        output_html = """
                        <div id="exp-method-box">
                            <div>%s</div>
                            
                            <div style="margin: 1em 0 0 9em;">
                                <div id="rolling-box">
                                    <div><label for="%s_%s">Period</label> %s %s</div>
                                    <div><label for="%s_%s">Expires On</label> %s</div>
                                    <div><label for="%s_%s">Renew Expires On</label> %s</div>
                                </div>
                                
                                <div id="fixed-box">
                                    <div><label for="%s_%s">Expires On</label> %s</div>
                                    <div>%s For option 2, grace period %s day(s) before expiration then expires next year</div>
                                </div>
                            </div>
                            
                        </div>
                      """ % (rendered_period_type, 
                           name, self.pos_d['period'],
                           rendered_period, rendered_period_unit,
                           name, self.pos_d['expiration_method'], rendered_expiration_method,
                           name, self.pos_d['renew_expiration_method'], rendered_renew_expiration_method,
                           name, self.pos_d['fixed_expiration_method'], rendered_fixed_expiration_method,
                           rendered_fixed_expiration_rollover, rendered_fixed_expiration_rollover_days)
                      
        return mark_safe(output_html)
        
        
        
    def render_widget(self, widget, name, value, attrs, index=0, id=None):
        i = index
        id_ = id
        if value:
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
        else:
            widget_value = None
        if id_:
            final_attrs = dict(attrs, id='%s_%s' % (id_, i))
        return widget.render(name+'_%s' %i, widget_value, final_attrs)
        
    
    def decompress(self, value):
        if value:
            return value.split(",")
        return None
        

class TypeExpMethodField(forms.MultiValueField):
    def __init__(self, required=True, widget=TypeExpMethodWidget(attrs=None),
                label=None, initial=None, help_text=None):
        myfields = (
                    #forms.CharField(max_length=10, label="Period"), 
                    #forms.ChoiceField(choices=PERIOD_UNIT_CHOICE),
                    )
        super(TypeExpMethodField, self).__init__(myfields, required, widget,
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
        
