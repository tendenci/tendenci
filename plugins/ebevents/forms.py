from django import forms
#from django.utils.translation import ugettext_lazy as _

MONTHS_CHOICES = (
                    ('0', 'Select Month'),
                    ('1', 'January'),
                    ('2', 'February'),
                    ('3', 'March'),
                    ('4', 'April'),
                    ('5', 'May'),
                    ('6', 'June'),
                    ('7', 'July'),
                    ('8', 'August'),
                    ('9', 'September'),
                    ('10', 'October'),
                    ('11', 'November'),
                    ('12', 'December'),
                    )

class EventSearchForm(forms.Form):
    event_month = forms.ChoiceField(required=False, choices=MONTHS_CHOICES)
    event_year = forms.ChoiceField(required=False)
    event_type = forms.ChoiceField(required=False)
    
    def __init__(self, *args, **kwargs): 
        super(EventSearchForm, self).__init__(*args, **kwargs)
        