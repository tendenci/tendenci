import datetime
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _
from tendenci.addons.campaign_monitor.models import Template
from tendenci.core.newsletters.models import NewsletterTemplate
from tendenci.apps.user_groups.models import Group

from .models import Newsletter

THIS_YEAR = datetime.date.today().year
DAYS_CHOICES = ((1,'1'), (3,'3'), (5,'5'), (7,'7'),
                (14,'14'), (30,'30'), (60,'60'), (90,'90'),
                (120,'120'), (0,'ALL'),
                )
INCLUDE_CHOICES = ((1, _('Include')),(0, _('Skip')),)

FORMAT_CHOICES = ((1, 'Detailed - original format View Example'), (0, 'Simplified - removes AUTHOR, POSTED BY, RELEASES DATE, etc from the detailed format View Example'))

types_list = [(u'',_(u'All'))]

DEFAULT_TEMPLATE_CHOICES = (
    ('newsletters/templates/default/Big City Newsletter.html', 'Big City Newsletter'),
    ('newsletters/templates/default/Holiday Night Lights Newsletter.html', 'Holiday Night Lights Newsletter'),
    ('newsletters/templates/default/One Column With Header.html', 'One Column With Header'),
    ('newsletters/templates/default/Seagulls Newsletter.html', 'Seagulls Newsletter'),
    ('newsletters/templates/default/Subway Line Newsletter.html', 'Subway Line Newsletter'),
    ('newsletters/templates/default/Two Column Left Newsletter.html', 'Two Column Left Newsletter'),
    ('newsletters/templates/default/Two Column Left Sidebar.html', 'Two Column Left Sidebar'),
    ('newsletters/templates/default/Two Column Right Sidebar.html', 'Two Column Right Sidebar'),
)

"""
Choices for Old Form (t4 version)
"""


try:
    from tendenci.addons.events.models import Type
    types = Type.objects.all()
    for type in types:
        types_list.append((int(type.pk),type.name))
except ImportError:
    pass
TYPE_CHOICES = tuple(types_list)

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


class OldGenerateForm(forms.Form):
    ### step 1 ###

    # recipient, subject fields
    member_only = forms.BooleanField()
    send_to_email2 = forms.BooleanField()
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, empty_label='SELECT ONE')
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': 50}), required=True)
    personalize_subject_first_name = forms.BooleanField()
    personalize_subject_last_name = forms.BooleanField()
    include_login = forms.BooleanField()

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

    #template
    template = forms.ChoiceField(choices=DEFAULT_TEMPLATE_CHOICES, widget=forms.RadioSelect)

    # format
    format = forms.ChoiceField(choices=FORMAT_CHOICES, widget=forms.RadioSelect)

    def generate_newsletter(self, template):
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

