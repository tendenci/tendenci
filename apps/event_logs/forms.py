from datetime import datetime, timedelta
from django.utils.translation import ugettext_lazy as _
from django import forms

from base.fields import SplitDateTimeField
from form_utils.forms import BetterForm

INITIAL_START_DT = datetime.now() - timedelta(weeks=4)
INITIAL_END_DT = datetime.now()


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
    start_dt = SplitDateTimeField(
        label=_('Start Date/Time'),
        initial=INITIAL_START_DT,
        required=False
    )
    end_dt = SplitDateTimeField(
        label=_('End Date/Time'),
        initial=INITIAL_END_DT,
        required=False
    )
    request_method = forms.ChoiceField(
        required=False,
        choices=(('all', 'ALL',), ('post', 'POST',), ('get', 'GET',))
    )
    event_id = forms.IntegerField(required=False)
    source = forms.CharField(required=False)
    object_id = forms.CharField(required=False)
    user_ip_address = forms.CharField(required=False)
    user_id = forms.IntegerField(required=False)
    user_name = forms.CharField(required=False)
    session_id = forms.CharField(required=False)

    class Meta:
        fields = (
            'start_dt',
            'end_dt',
            'request_method',
            'event_id',
            'source',
            'object_id'
            'user_ip_address',
            'user_id',
            'user_name',
            'session_id',
            )

        fieldsets = [('',
            {
              'fields': ['start_dt',
                         'end_dt',
                         'request_method',
                         'event_id'
                         ],
              'legend': ''
              }),
            ('Advanced Options',
            {
              'fields': ['user_id',
                         'user_name',
                         'user_ip_address',
                         'session_id',
                         'source',
                         'object_id'
                         ],
              'legend': 'Advanced Options'
              }),
        ]
