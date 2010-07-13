from django import forms

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