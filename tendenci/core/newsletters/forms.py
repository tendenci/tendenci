import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template import RequestContext

from tendenci.core.emails.models import Email
from tendenci.addons.campaign_monitor.models import Template
from tendenci.core.perms.utils import has_perm
from tendenci.core.base.http import Http403
from tendenci.core.newsletters.models import NewsletterTemplate, Newsletter
from tendenci.core.newsletters.models import (
    THIS_YEAR,
    DAYS_CHOICES,
    INCLUDE_CHOICES,
    TYPE_CHOICES
)


class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        exclude = ["template_id", "create_date", "update_date", "cm_preview_url", "cm_screenshot_url"]

    zip_file = forms.FileField(required=False)


class GenerateForm(forms.Form):
    # module content
    jump_links = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    events =  forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    event_start_dt = forms.DateField(initial=datetime.date.today(), widget=SelectDateWidget(None, range(1920, THIS_YEAR+10)))
    event_end_dt = forms.DateField(initial=datetime.date.today() + datetime.timedelta(days=90), widget=SelectDateWidget(None, range(1920, THIS_YEAR+10)))
    events_type = forms.ChoiceField(initial='', choices=TYPE_CHOICES, required=False)
    articles = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    articles_days = forms.ChoiceField(initial=60, choices=DAYS_CHOICES)
    news = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    news_days = forms.ChoiceField(initial=30, choices=DAYS_CHOICES)
    jobs = forms.ChoiceField(initial=1, choices=INCLUDE_CHOICES)
    jobs_days = forms.ChoiceField(initial=30, choices=DAYS_CHOICES)
    pages = forms.ChoiceField(initial=0, choices=INCLUDE_CHOICES)
    pages_days = forms.ChoiceField(initial=7, choices=DAYS_CHOICES)

    #Campaign Monitor Template
    template = forms.ModelChoiceField(queryset=NewsletterTemplate.objects.all())


class OldGenerateForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        widgets = {
            'subject': forms.TextInput(attrs={'size': 50}),
            'event_start_dt': SelectDateWidget(None, range(1920, THIS_YEAR+10)),
            'event_end_dt': SelectDateWidget(None, range(1920, THIS_YEAR+10)),
            'default_template': forms.RadioSelect,
            'format': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(OldGenerateForm, self).__init__(*args, **kwargs)
        self.fields['default_template'].blank = False
        self.fields['email'].required = False
        self.fields['group'].empty_label = _('SELECT ONE')

    def clean_group(self):
        data = self.cleaned_data
        group = data.get('group', None)
        member_only = data.get('member_only', False)

        if not member_only and not group:
            raise forms.ValidationError(_('Usergroup field is required if Send to members only is unchecked.'))

        return group

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        subject = ''
        subj = data.get('subject', '')
        inc_last_name = data.get('personalize_subject_last_name')
        inc_first_name = data.get('personalize_subject_first_name')

        if inc_first_name and not inc_last_name:
            subject = '[firstname] ' + subj
        elif inc_last_name and not inc_first_name:
            subject = '[lastname] ' + subj
        elif inc_first_name and inc_last_name:
            subject = '[firstname] [lastname] ' + subj
        else:
            subject = subj
        nl = super(OldGenerateForm, self).save(*args, **kwargs)
        nl.subject = subject
        if nl.default_template:
            template = render_to_string(nl.default_template, context_instance=RequestContext(self.request))
            email_content = nl.generate_newsletter(self.request, template)

            email = Email()
            email.subject = subject
            email.body = email_content
            email.sender = self.request.user.email
            email.sender_display = self.request.user.profile.get_name()
            email.reply_to = self.request.user.email
            email.creator = self.request.user
            email.creator_username = self.request.user.username
            email.owner = self.request.user
            email.owner_username = self.request.user.username
            email.save()
            nl.email = email

        nl.save()

        return nl
