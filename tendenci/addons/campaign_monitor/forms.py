import datetime
from django import forms
from django.conf import settings
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _
from tendenci.addons.campaign_monitor.models import Template, Campaign, ListMap
from createsend import CreateSend
from createsend import Campaign as CSC

THIS_YEAR = datetime.date.today().year
DAYS_CHOICES = ((1,'1'), (3,'3'), (5,'5'), (7,'7'),
                (14,'14'), (30,'30'), (60,'60'), (90,'90'),
                (120,'120'), (0,'ALL'),
                )
INCLUDE_CHOICES = ((1, _('Include')),(0, _('Skip')),)


types_list = [('',_('All'))]
try:
    from tendenci.addons.events.models import Type
    types = Type.objects.all()
    for type in types:
        types_list.append((int(type.pk),type.name))
except ImportError:
    pass
TYPE_CHOICES = tuple(types_list)

api_key = getattr(settings, 'CAMPAIGNMONITOR_API_KEY', None)
client_id = getattr(settings, 'CAMPAIGNMONITOR_API_CLIENT_ID', None)
CreateSend.api_key = api_key

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        exclude = ["template_id", "create_date", "update_date", "cm_preview_url", "cm_screenshot_url"]

    zip_file = forms.FileField(required=False)

class CampaignForm(forms.Form):
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
    template = forms.ModelChoiceField(queryset=Template.objects.all())


