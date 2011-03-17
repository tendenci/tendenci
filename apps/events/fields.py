from datetime import datetime, timedelta
from django.template.defaultfilters import date as date_filter
from django.forms import ChoiceField
from django.forms.widgets import Widget, TextInput
from django.utils.safestring import mark_safe
from base.widgets import SplitDateTimeWidget


def reg8n_dt_choices(instance):
    """
    Return a tuple of 2-tuples.
    Registration datetimes (machine_name, human_name).
    """

    if not instance:
        return tuple()

    return {
        'early_price':instance.early_price,
        'regular_price':instance.regular_price,
        'late_price':instance.late_price,
        'early_dt':instance.early_dt,
        'regular_dt':instance.regular_dt,
        'late_dt':instance.late_dt,
        'end_dt':instance.end_dt,
    }.items()

class Reg8nDtWidget(Widget):
    def render(self, name, value, attrs=None, choices=()):
        choices = dict(self.choices)

        # prices
        early_price = choices.get('early_price') or 0
        regular_price = choices.get('regular_price') or 0
        late_price = choices.get('late_price') or 0

        today = datetime.today()

        # # datetimes
        early_dt = choices.get('early_dt') or today
        regular_dt = choices.get('regular_dt') or today + timedelta(days=1)
        late_dt = choices.get('late_dt') or today + timedelta(days=2)
        end_dt = choices.get('end_dt') or today + timedelta(days=3)

        # start widgets
        text_widget = TextInput({'class':'reg8n_price'})
        dt_widget = SplitDateTimeWidget()

        # string format dict
        str_format_kwargs = {
            'early_price': text_widget.render('regconf-early_price', early_price),
            'regular_price': text_widget.render('regconf-regular_price', regular_price),
            'late_price': text_widget.render('regconf-late_price', late_price),
            'early_dt': dt_widget.render('regconf-early_dt', early_dt),
            'regular_dt': dt_widget.render('regconf-regular_dt', regular_dt),
            'late_dt': dt_widget.render('regconf-late_dt', late_dt),
            'end_dt': dt_widget.render('regconf-end_dt', end_dt),
        }

        # string format template
        # html  = u"""
        #     <div>Registration opens on %(early_dt)s</div>
        #     <div>Pay %(early_price)s until %(regular_dt)s</div>
        #     <div>Pay %(regular_price)s until %(late_dt)s</div>
        #     <div>Pay %(late_price)s until registration closes on %(end_dt)s</div>
        # """ % str_format_kwargs

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
    