from datetime import datetime, timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.corporate_memberships.notices.utils import get_membership_notice_choices

class NoticeLogSearchForm(forms.Form):
    start_dt = forms.SplitDateTimeField(label=_('Sent Start Date/Time'),
        initial=(datetime.now()-timedelta(days=30)), required=False)
    end_dt = forms.SplitDateTimeField(label=_('Sent End Date/Time'),
        initial=datetime.now(), required=False)
    notice_id = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super(NoticeLogSearchForm, self).__init__(*args, **kwargs)
        self.fields['notice_id'].choices = get_membership_notice_choices()
