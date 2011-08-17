import datetime
from django import forms
from django.forms.widgets import RadioFieldRenderer, RadioInput
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.forms.util import flatatt
from memberships.models import NOTICE_TYPES


PERIOD_UNIT_CHOICE = (
                      ("days", _("Day(s)")),
                      ("months", _("Month(s)")),
                      ("years", _("Year(s)")),)
PERIOD_CHOICES = (
                  ("fixed", _("Fixed")),
                  ("rolling", _("Rolling")),
                  )
MONTHS_CHOICES = (
                    ('1', 'Jan (01)'),
                    ('2', 'Feb (02)'),
                    ('3', 'Mar (03)'),
                    ('4', 'Apr (04)'),
                    ('5', 'May (05)'),
                    ('6', 'Jun (06)'),
                    ('7', 'Jul (07)'),
                    ('8', 'Aug (08)'),
                    ('9', 'Sep (09)'),
                    ('10', 'Oct (10)'),
                    ('11', 'Nov (11)'),
                    ('12', 'Dec (12)'),
                    )
DAYS_CHOICES = [(day, day) for day in range(1, 32)]
    
class TypeExpMethodWidget(forms.MultiWidget):
    def __init__(self, attrs=None, fields_pos_d=None):
        self.attrs = attrs
        self.pos_d = fields_pos_d
        #self.pos_d = {'period_type': (0, forms.Select()),
        #              'period': (1, forms.TextInput()),
        #              'period_unit':(2, forms.Select()),
        #              'rolling_option':(3, forms.RadioSelect()),
        #              'rolling_option1_day':(4, forms.TextInput()),
        #              'rolling_renew_option':(5, forms.RadioSelect()),
        #              'rolling_renew_option1_day':(6, forms.TextInput()),
        #              'rolling_renew_option2_day':(7, forms.TextInput()),
        #              'fixed_option':(8, forms.RadioSelect()),
        #              'fixed_option1_day':(9, forms.Select()),
        #              'fixed_option1_month':(10, forms.Select()),
        #              'fixed_option1_year':(11, forms.Select()),
        #              'fixed_option2_day':(12, forms.Select()),
        #              'fixed_option2_month':(13, forms.Select()),
        #              'fixed_option2_can_rollover':(14, forms.CheckboxInput()),
        #              'fixed_option2_rollover_days':(15, forms.TextInput()),
        #               }
        self.widgets = ()
        if self.pos_d:
            items = self.pos_d.values()
            items.sort()
            self.widgets = [item[1] for item in items]
            
        super(TypeExpMethodWidget, self).__init__(self.widgets, attrs)
    
    def render(self, name, value, attrs=None):
        if not isinstance(value, list):
            value = self.decompress(value)
            
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        
        # period type
        period_type_widget = self.pos_d['period_type'][1]
        period_type_widget.choices = PERIOD_CHOICES
        #self.widgets.append(period_type_widget)
        rendered_period_type = self.render_widget(period_type_widget, 
                                                  name, value, final_attrs, self.pos_d['period_type'][0], id_)
        
        # period
        period_widget = self.pos_d['period'][1]
        period_widget.attrs = {'size':'8'}
        rendered_period = self.render_widget(period_widget, name, value, final_attrs, 
                                             self.pos_d['period'][0], id_)
        # period_unit
        period_unit_widget = self.pos_d['period_unit'][1]
        period_unit_widget.choices = PERIOD_UNIT_CHOICE
        rendered_period_unit = self.render_widget(period_unit_widget, 
                                                  name, value, final_attrs, self.pos_d['period_unit'][0], id_)
        # expiration_method_day
        rolling_option1_day_widget = self.pos_d['rolling_option1_day'][1]
        rolling_option1_day_widget.attrs = {'size':'8'}
        rendered_rolling_option1_day = self.render_widget(rolling_option1_day_widget, 
                                                            name, value, final_attrs, 
                                                            self.pos_d['rolling_option1_day'][0], id_)
        # expiration_method
        JOIN_EXP_METHOD_CHOICE = (
                                  ("0", "End of full period"),
                                  ("1", mark_safe("%s day(s) at signup month" % \
                                                  rendered_rolling_option1_day)),)
        rolling_option_widget = self.pos_d['rolling_option'][1]
        rolling_option_widget.choices=JOIN_EXP_METHOD_CHOICE
        rendered_rolling_option = self.render_widget(rolling_option_widget, 
                                                  name, value, final_attrs, 
                                                  self.pos_d['rolling_option'][0], id_)
        
        # rolling_renew_option1_day
        rolling_renew_option1_day_widget = self.pos_d['rolling_renew_option1_day'][1]
        rolling_renew_option1_day_widget.attrs = {'size':'8'}
        rendered_rolling_renew_option1_day = self.render_widget(rolling_renew_option1_day_widget, 
                                                            name, value, final_attrs, 
                                                            self.pos_d['rolling_renew_option1_day'][0], id_)
        # renew_expiration_day2
        rolling_renew_option2_day_widget = self.pos_d['rolling_renew_option2_day'][1]
        rolling_renew_option2_day_widget.attrs = {'size':'8'}
        rendered_rolling_renew_option2_day = self.render_widget(rolling_renew_option2_day_widget, 
                                                            name, value, final_attrs, 
                                                           self.pos_d['rolling_renew_option2_day'][0], id_)
        # renew_expiration_method
        RENEW_EXP_METHOD_CHOICE = (
                                  ("0", "End of full period"),
                                  ("1", mark_safe("%s day(s) at signup month" % \
                                                  rendered_rolling_renew_option1_day)),
                                  ("2", mark_safe("%s day(s) at renewal month" % \
                                                  rendered_rolling_renew_option2_day)),)
        rolling_renew_option_widget = self.pos_d['rolling_renew_option'][1]
        rolling_renew_option_widget.choices=RENEW_EXP_METHOD_CHOICE
        rendered_rolling_renew_option = self.render_widget(rolling_renew_option_widget, 
                                                  name, value, final_attrs, 
                                                  self.pos_d['rolling_renew_option'][0], id_)
        # fixed_option1_day
        fixed_option1_day_widget = self.pos_d['fixed_option1_day'][1]
        fixed_option1_day_widget.choices=DAYS_CHOICES
        rendered_fixed_option1_day = self.render_widget(fixed_option1_day_widget, 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_option1_day'][0], id_)
        # fixed_option1_month
        fixed_option1_month_widget = self.pos_d['fixed_option1_month'][1]
        fixed_option1_month_widget.choices=MONTHS_CHOICES
        rendered_fixed_option1_month = self.render_widget(fixed_option1_month_widget, 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_option1_month'][0], id_)
        # dynamically generate the year choices for fixed_option1_year
        fixed_option1_year = ''
        if value:
            try:
                fixed_option1_year = int(value[self.pos_d['fixed_option1_year'][0]])
            except:
                pass
        if not fixed_option1_year:
            fixed_option1_year = int(datetime.date.today().year)
        years = [(year, year) for year in range(fixed_option1_year-1, fixed_option1_year+20)]

        #fixed_expiration_year
        fixed_option1_year_widget =  self.pos_d['fixed_option1_year'][1]
        fixed_option1_year_widget.choices=years
        rendered_fixed_option1_year = self.render_widget(fixed_option1_year_widget, 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_option1_year'][0], id_)
        # fixed_option2_day
        fixed_option2_day_widget = self.pos_d['fixed_option2_day'][1]
        fixed_option2_day_widget.choices=DAYS_CHOICES
        rendered_fixed_option2_day = self.render_widget(fixed_option2_day_widget, 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_option2_day'][0], id_)
        #fixed_option2_month
        fixed_option2_month_widget = self.pos_d['fixed_option2_month'][1]
        fixed_option2_month_widget.choices=MONTHS_CHOICES
        rendered_fixed_option2_month = self.render_widget(fixed_option2_month_widget, 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_option2_month'][0], id_)
        FIXED_EXP_METHOD_CHOICE = (
                                  ("0", mark_safe("%s %s %s" % (rendered_fixed_option1_month,
                                                      rendered_fixed_option1_day,
                                                      rendered_fixed_option1_year))),
                                  ("1", mark_safe("%s %s of current year" % \
                                                  (rendered_fixed_option2_month,
                                                   rendered_fixed_option2_day))))
        
        # fixed_option
        fixed_option_widget = self.pos_d['fixed_option'][1]  
        fixed_option_widget.choices=FIXED_EXP_METHOD_CHOICE                     
        rendered_fixed_option = self.render_widget(fixed_option_widget, 
                                                  name, value, final_attrs, 
                                                  self.pos_d['fixed_option'][0], id_)
        # fixed_option2_rollover_days
        fixed_option2_rollover_days_widget = self.pos_d['fixed_option2_rollover_days'][1]
        fixed_option2_rollover_days_widget.attrs={'size':'8'}
        rendered_fixed_option2_rollover_days = self.render_widget(fixed_option2_rollover_days_widget, 
                                                            name, value, final_attrs, 
                                                            self.pos_d['fixed_option2_rollover_days'][0], id_)
        # fixed_option2_can_rollover
        fixed_option2_can_rollover_widget = self.pos_d['fixed_option2_can_rollover'][1]
        rendered_fixed_option2_can_rollover = self.render_widget(fixed_option2_can_rollover_widget,
                                                       name, value, final_attrs, 
                                                       self.pos_d['fixed_option2_can_rollover'][0], id_)
        
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
                                    <div>%s For option 2, grace period %s day(s) before expiration then expires in the next year</div>
                                </div>
                            </div>
                            
                        </div>
                      """ % (rendered_period_type, 
                           name, self.pos_d['period'],
                           rendered_period, rendered_period_unit,
                           name, self.pos_d['rolling_option'], rendered_rolling_option,
                           name, self.pos_d['rolling_renew_option'], rendered_rolling_renew_option,
                           name, self.pos_d['fixed_option'], rendered_fixed_option,
                           rendered_fixed_option2_can_rollover, rendered_fixed_option2_rollover_days)
                      
        return mark_safe(output_html)
        
        
        
    def render_widget(self, widget, name, value, attrs, index=0, id=None):
        i = index
        id_ = id
        if value:
            try:
                widget_value = value[i]
            except IndexError:
                self.fields['type_exp_method'].initial = None
        else:
            widget_value = None
        if id_:
            final_attrs = dict(attrs, id='%s_%s' % (id_, i))

        return widget.render(name+'_%s' %i, widget_value, final_attrs)
        
    
    def decompress(self, value):
        if value:
            return value.split(",")
        return None
    
class NoticeTimeTypeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        self.attrs = attrs
        self.pos_d = {'num_days': (0, forms.TextInput()),
                      'notice_time': (1, forms.Select()),
                      'notice_type':(2, forms.Select()),
                       }
        self.widgets = ()
        if self.pos_d:
            items = self.pos_d.values()
            items.sort()
            self.widgets = [item[1] for item in items]
            
        super(NoticeTimeTypeWidget, self).__init__(self.widgets, attrs)
    
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
        
        # notice_time
        notice_time_widget = self.pos_d['notice_time'][1]
        notice_time_widget.choices = (('after','After'),
                                      ('before','Before'),
                                      ('attimeof','At Time Of'))
        rendered_notice_time = self.render_widget(notice_time_widget, 
                                                  name, value, final_attrs, self.pos_d['notice_time'][0], id_)
        
        # notice_type
        notice_type_widget = self.pos_d['notice_type'][1]
        notice_type_widget.choices = NOTICE_TYPES
        rendered_notice_type = self.render_widget(
            notice_type_widget,name,value,final_attrs,
            self.pos_d['notice_type'][0],id
        )
        
        output_html = """
                        <div id="notice-time-type">
                            %s day(s) %s %s
                        </div>
                      """ % (rendered_num_days,
                             rendered_notice_time,
                             rendered_notice_type
                             )
                      
        return mark_safe(output_html)
        
        
        
    def render_widget(self, widget, name, value, attrs, index=0, id=None):
        i = index
        id_ = id
        if value:
            try:
                widget_value = value[i]
            except IndexError:
                self.fields['notice_time_type'].initial = None
        else:
            widget_value = None
        if id_:
            final_attrs = dict(attrs, id='%s_%s' % (id_, i))

        return widget.render(name+'_%s' %i, widget_value, final_attrs)
        
    
    def decompress(self, value):
        if value:
            return value.split(",")
        return None

# removed the label when any of the radio select contains another input field
class CustomRadioInput(RadioInput):
    def __unicode__(self):
        #if 'id' in self.attrs:
        #    label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        #else:
        #    label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'%s %s' % (self.tag(), choice_label))


class CustomRadioFieldRenderer(RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield CustomRadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return CustomRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)

class CustomRadioSelect(forms.RadioSelect):
    renderer = CustomRadioFieldRenderer

class Output(forms.Widget):
    """
    Base class for all <output> widgets (e.g. titles and paragraphs).
    These are fake-fields; they do not take input.
    """

    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return force_unicode(self._format_value(value))

class Header(Output):
    """
    Outputs text.  Using class name to identify the type
    of text that is being output.
    """

class Description(Output):
    """
    Outputs text.  Using class name to identify the type
    of text that is being output.
    """

class HorizontalRule(Output):
    """
    Outputs text.  Using class name to identify the type
    of text that is being output.
    """