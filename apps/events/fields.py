from datetime import datetime, timedelta
from django.http import QueryDict
from django.forms import ChoiceField
from django.forms.widgets import Widget, TextInput
from django.utils.safestring import mark_safe
from django.template.defaultfilters import date as date_filter
from base.widgets import SplitDateTimeWidget


def reg8n_dt_choices(*args, **kwargs):
    """
    Use values from query_dict or instance.
    Return 2-tuple of reg8n items.
    """
    instance = kwargs.get('instance')
    prefix = kwargs.get('prefix')
    query_dict = None

    if args and args[0]:
        query_dict = args[0]

    # save ourselves from looping
    if not instance and not query_dict:
        return tuple()

    return_kwargs = {
        'early_price': u'',
        'regular_price': u'',
        'late_price': u'',
        'early_dt': u'',
        'regular_dt': u'',
        'late_dt': u'',
        'end_dt': u'',
    }

    for k, v in return_kwargs.items():
        if query_dict:

            if k[-2:] == 'dt':  # if datetime variable
                str_date = query_dict.get('%s-%s_0' % (prefix, k))
                str_time = query_dict.get('%s-%s_1' % (prefix, k))
                return_kwargs[k] = datetime.strptime('%s %s' % (str_date, str_time), '%Y-%m-%d %I:%M %p')
            else:
                return_kwargs[k] = query_dict.get('%s-%s' % (prefix, k))

        elif instance and hasattr(instance, k):
            return_kwargs[k] = getattr(instance, k)

    return return_kwargs.items()

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
    