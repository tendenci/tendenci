from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
from django import forms

from tendenci.libs.form_utils.forms import BetterForm
from tendenci.apps.base.forms import FormControlWidgetMixin

from .utils import get_app_list_choices

REQUEST_CHOICES = [('all', _('ALL'),), ('post', _('POST'),), ('get', _('GET'),)]
APP_CHOICES = get_app_list_choices()


class EventsFilterForm(forms.Form):
    event_id = forms.IntegerField(required=False)
    ip = forms.CharField(max_length=16, required=False)
    user_id = forms.IntegerField(required=False)
    session_id = forms.CharField(max_length=40, required=False)

    def process_filter(self, queryset):
        cd = self.cleaned_data
        if cd['event_id']:
            queryset = queryset.filter(event_id=cd['event_id'])
        if cd['ip']:
            queryset = queryset.filter(user_ip_address=cd['ip'])
        if cd['user_id']:
            queryset = queryset.filter(user__pk=cd['user_id'])
        if cd['session_id']:
            queryset = queryset.filter(session_id=cd['session_id'])
        return queryset


class EventLogSearchForm(BetterForm):
    start_dt = forms.SplitDateTimeField(
        label=_('Start Date/Time'),
        required=False,
        input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
        input_time_formats=['%I:%M %p', '%H:%M:%S']
    )
    end_dt = forms.SplitDateTimeField(
        label=_('End Date/Time'),
        required=False,
        input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
        input_time_formats=['%I:%M %p', '%H:%M:%S']
    )
    request_method = forms.ChoiceField(
        required=False,
        choices=REQUEST_CHOICES,
        help_text=_('GET = whether a page/item was viewed. POST = an item was edited or added')
      )

    object_id = forms.IntegerField(
        min_value=1,
        required=False,
        help_text=_("This is the ID Tendenci uses for all objects. "
        "This is the number you sometimes see in URLs. For example, "
        "for the event at http://tendenci.com/events/173/, the object ID is 173."))

    user_ip_address = forms.CharField(required=False)
    user_id = forms.IntegerField(required=False)
    user_name = forms.CharField(required=False)

    application = forms.ChoiceField(
        required=False,
        choices=APP_CHOICES,
        help_text=_("These are the different modules like Pages or Articles."))

    action = forms.CharField(
      required=False,
      help_text=_("These are the actions within the python commands at view.py. "
      "Some examples of actions are search and edit, for example.")
      )

    class Meta:
        fields = (
            'start_dt',
            'end_dt',
            'request_method',
            'object_id'
            'user_ip_address',
            'user_id',
            'user_name',
            'application',
            'action',
            )

        fieldsets = [('',
            {
              'fields': ['start_dt',
                         'end_dt',
                         'request_method',
                         ],
              'legend': ''
              }),
            (_('Advanced Options'),
            {
              'fields': ['user_id',
                         'user_name',
                         'user_ip_address',
                         'object_id',
                         'application',
                         'action'
                         ],
              'legend': 'Advanced Options'
              }),
        ]

    def __init__(self, *args, **kwargs):
        super(EventLogSearchForm, self).__init__(*args, **kwargs)
        self.fields['start_dt'].initial = datetime.now() - timedelta(weeks=4)
        self.fields['end_dt'].initial = datetime.now()
