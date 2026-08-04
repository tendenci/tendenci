from datetime import timedelta

from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from tendenci.apps.corporate_memberships.notices.utils import get_membership_notice_choices

class NoticeLogSearchForm(forms.Form):
    start_dt = forms.SplitDateTimeField(label=_('Sent Start Date/Time'),
        initial=(timezone.now()-timedelta(days=30)), required=False)
    end_dt = forms.SplitDateTimeField(label=_('Sent End Date/Time'),
        initial=timezone.now(), required=False)
    notice_id = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notice_id'].choices = get_membership_notice_choices()
