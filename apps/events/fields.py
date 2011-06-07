from ordereddict import OrderedDict

from datetime import datetime, timedelta
from django.http import QueryDict
from django.forms import ChoiceField
from django.forms.widgets import Widget, TextInput
from django.utils.safestring import mark_safe
from django.template.defaultfilters import date as date_filter

from base.widgets import SplitDateTimeWidget


class Reg8nDtWidget(Widget):

    reg8n_dict = {
        'early_price': '',
        'regular_price': '',
        'late_price': '',
        'early_dt': '',
        'regular_dt': '',
        'late_dt': '',
        'end_dt': '',
    }

    def render(self, name, value, attrs=None, choices=()):
        # rip prefix from name
        name_prefix = name.split('-')
        
        # This is a little hacky, and doesn't
        # compensate for dashes in a prefix
        # If you put dashes in a prefix, you're fired
        if len(name_prefix) > 2:
            # prefixes for form sets
            # Prefix = eloy
            # Field Name = eloy-0-fieldname .. eloy-N-fieldname
            prefix = '%s-%s' % (
                name_prefix[0],
                name_prefix[1]
            )
        else:
            # prefix for non-formsets
            # Prefix = eloy
            # Field Name = eloy-fieldname
            prefix = name_prefix[0]

        str_format_kwargs = []
        for k, v in self.reg8n_dict.items():
            if k.split('_')[1] == 'price':
                # text field
                str_format_kwargs.append(TextInput().render(
                    '%s' % (k),  # name
                    self.reg8n_dict.get(k),  # value
                    {
                        'id': '%s' % (k),
                    }  # id attribute
                ))

            elif k.split('_')[1] == 'dt':
                # date field
                str_format_kwargs.append(SplitDateTimeWidget().render(
                    '%s' % (k),  # name
                    self.reg8n_dict.get(k),  # value
                    {
                        'id': '%s' % (k)
                    }  # id attribute
                ))

        # string format template
        html  = u"""
            <div>%s after %s</div>
            <div>%s after %s</div>
            <div>%s after %s</div>
            <div>registration ends %s</div>
            """ % tuple(str_format_kwargs)

        return mark_safe(html)


class Reg8nDtField(ChoiceField): 
    """
        Inherits from MultipleChoiceField and
        sets some default meta data
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
        instance = kwargs.get('instance')
        prefix = kwargs.get('prefix')
        initial = kwargs.get('initial') or {}
        query_dict = {}

        if args and args[0]:
            query_dict = args[0]

        today = datetime.today()
        one_hour = timedelta(hours=1)

        if prefix:
            reg8n_dict = OrderedDict([
                ('%s-early_price' % prefix, initial.get('early_price') or 0),
                ('%s-early_dt' % prefix, initial.get('early_dt') or today),
                ('%s-regular_price' % prefix, initial.get('regular_price') or 0),
                ('%s-regular_dt' % prefix, initial.get('regular_dt') or (today+one_hour)),  # 1 hr
                ('%s-late_price' % prefix, initial.get('late_price') or 0),      
                ('%s-late_dt' % prefix, initial.get('late_dt') or (today+(one_hour*2))),  # 2 hrs
                ('%s-end_dt' % prefix, initial.get('end_dt') or (today+(one_hour*3))),  # 3 hrs
            ])
        else:
             reg8n_dict = OrderedDict([
                ('early_price', initial.get('early_price') or 0),
                ('early_dt', initial.get('early_dt') or today),
                ('regular_price', initial.get('regular_price') or 0),
                ('regular_dt', initial.get('regular_dt') or (today+one_hour)),  # 1 hr
                ('late_price', initial.get('late_price') or 0),
                ('late_dt', initial.get('late_dt') or (today+(one_hour*2))),  # 2 hrs
                ('end_dt', initial.get('end_dt') or (today+(one_hour*3))),  # 3 hrs
            ])

        # save ourselves from looping; no need
        if not query_dict and not instance:
            self.widget.reg8n_dict = reg8n_dict
            return reg8n_dict

        # edit page pre-population of the form fields
        for k, v in reg8n_dict.items():
            original_key = k
            # for formsets
            if prefix:
                k = k.replace('%s-' % prefix, '')
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
                    if prefix:
                        reg8n_dict[original_key] = getattr(instance, k)
                    else:
                        reg8n_dict[k] = getattr(instance, k)

        self.widget.reg8n_dict = reg8n_dict
        return reg8n_dict
