import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template import RequestContext

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
        self.fields['content'].required = False

    def save(self, *args, **kwargs):
        nl = super(OldGenerateForm, self).save(*args, **kwargs)
        if nl.default_template:
            nl.content = render_to_string(nl.default_template, context_instance=RequestContext(self.request))

        nl.save()

        return nl