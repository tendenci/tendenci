import datetime

from django.conf import settings
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template import RequestContext

from tendenci.apps.emails.models import Email
from tendenci.apps.campaign_monitor.models import Template
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.base.http import Http403
from tendenci.apps.newsletters.utils import get_type_choices, is_newsletter_relay_set
from tendenci.apps.newsletters.models import NewsletterTemplate, Newsletter
from tendenci.apps.newsletters.models import (
    THIS_YEAR,
    DAYS_CHOICES,
    INCLUDE_CHOICES
)

EMAIL_SEARCH_CRITERIA_CHOICES = (
    ('subject__icontains', _('Subject')),
    ('id', _('Email ID #')),
    ('sender__icontains', _('Sender')),
    ('body__icontains', _('Body of Email')),
    ('owner__id', _('Owner User ID #')),
    ('owner_username', _('Owner Username')),
    ('creator__id', _('Creator User ID #')),
    ('creator_username', _('Creator Username'))
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
    events_type = forms.ChoiceField(initial='', choices=get_type_choices(), required=False)
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
        fields = "__all__"
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
        not_required = ['actionname', 'actiontype', 'article', 'send_status',
        'date_created', 'date_submitted', 'date_email_sent', 'email_sent_count',
        'date_last_resent', 'resend_count']
        self.fields['default_template'].blank = False
        self.fields['email'].required = False
        self.fields['group'].empty_label = _('SELECT ONE')

        for key in not_required:
            self.fields[key].required = False

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
        nl.actionname = subject
        nl.date_created = datetime.datetime.now()
        nl.send_status = 'draft'
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


class MarketingStepOneForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields= ('actiontype', 'actionname',)

    def __init__(self, *args, **kwargs):
        super(MarketingStepOneForm, self).__init__(*args, **kwargs)
        self.fields['actiontype'].required = True
        self.fields['actionname'].required = True


class MarketingStepThreeForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('member_only', 'group',)

    def clean_group(self):
        data = self.cleaned_data
        group = data.get('group', None)
        member_only = data.get('member_only', False)

        if not member_only and not group:
            raise forms.ValidationError(_('Usergroup field is required if Send to members only is unchecked.'))

        return group


class MarketingStepFourForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('send_to_email2', 'sla',)

    def __init__(self, *args, **kwargs):
        super(MarketingStepFourForm, self).__init__(*args, **kwargs)
        self.fields['sla'].required = True

        self.fields['send_to_email2'] = forms.ChoiceField(
            choices=(
                (True, _('Yes')),
                (False, _('No')),
                ),
            label=_('include emal2'))


class MarketingStepFiveForm(forms.ModelForm):
    create_article = forms.BooleanField(label=_('Create an Article from this Newsletter?'), required=False)
    class Meta:
        model = Newsletter
        fields = ('create_article', 'send_status',)

    def clean(self):
        data = self.cleaned_data

        # check if email host relay is properly set up
        if not is_newsletter_relay_set():
            raise forms.ValidationError(_('Email relay is not configured properly.'
                                            ' Newsletter cannot be sent.'))

        return data

    def save(self, *args, **kwargs):
        create_article = self.cleaned_data.get('create_article', False)
        newsletter = super(MarketingStepFiveForm, self).save(*args, **kwargs)
        newsletter.date_submitted = datetime.datetime.now()
        newsletter.save()

        if create_article:
            newsletter.generate_article(newsletter.email.creator)

        newsletter.send_to_recipients()

        return newsletter


class NewslettterEmailUpdateForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('email',)


class MarketingStep2EmailFilterForm(forms.Form):
    search_criteria = forms.ChoiceField(choices=EMAIL_SEARCH_CRITERIA_CHOICES)
    q = forms.CharField(required=False)

    def filter_email(self, request, queryset):
        search_criteria = request.GET.get('search_criteria')
        q = request.GET.get('q')
        query = {search_criteria: q}
        queryset = queryset.filter(**query)

        return queryset



