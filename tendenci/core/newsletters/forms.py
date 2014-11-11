import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.template import RequestContext
from django.template import Template as DTemplate
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.shortcuts import render_to_response

from tendenci.addons.campaign_monitor.models import Template
from tendenci.core.perms.utils import has_perm
from tendenci.core.newsletters.utils import apply_template_media
from tendenci.core.base.http import Http403
from tendenci.core.newsletters.models import NewsletterTemplate
from tendenci.core.newsletters.utils import (
    newsletter_articles_list,
    newsletter_jobs_list,
    newsletter_news_list,
    newsletter_pages_list,
    newsletter_events_list)
from tendenci.apps.user_groups.models import Group


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

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(OldGenerateForm, self).__init__(*args, **kwargs)

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

        request = self.request

        if not has_perm(request.user, 'newsletters.view_newslettertemplate'):
            raise Http403

        simplified = True
        login_content = ""
        include_login = int(data.get('include_login', 0))
        if include_login:
            login_content = render_to_string('newsletters/login.txt',
                                             context_instance=RequestContext(request))

        jumplink_content = ""
        jump_links = int(data.get('jump_links', 1))
        if jump_links:
            jumplink_content = render_to_string('newsletters/jumplinks.txt', locals(),
                                                context_instance=RequestContext(request))

        art_content = ""
        articles = int(data.get('articles', 1))
        articles_days = data.get('articles_days', 60)
        if articles:
            articles_list, articles_content = newsletter_articles_list(request, articles_days, simplified)

        news_content = ""
        news = int(data.get('news', 1))
        news_days = data.get('news_days', 30)
        if news:
            news_list, news_content = newsletter_news_list(request, news_days, simplified)

        jobs_content = ""
        jobs = int(data.get('jobs', 1))
        jobs_days = data.get('jobs_days', 30)
        if jobs:
            jobs_list, jobs_content = newsletter_jobs_list(request, jobs_days, simplified)

        pages_content = ""
        pages = int(data.get('pages', 0))
        pages_days = data.get('pages_days', 7)
        if pages:
            pages_list, pages_content = newsletter_pages_list(request, pages_days, simplified)

        try:
            events = int(data.get('events', 1))
            events_type = data.get('events_type')
            start_y, start_m, start_d = data.get('event_start_dt', str(datetime.date.today())).split('-')
            event_start_dt = datetime.date(int(start_y), int(start_m), int(start_d))

            end_y, end_m, end_d = data.get(
                'event_end_dt',
                str(datetime.date.today() + datetime.timedelta(days=90))).split('-')
            event_end_dt = datetime.date(int(end_y), int(end_m), int(end_d))

            events_list, events_content = newsletter_events_list(
                request,
                start_dt=event_start_dt,
                end_dt=event_end_dt,
                simplified=simplified)

        except ImportError:
            events_list = []
            events_type = None

        text = DTemplate(apply_template_media(template))
        context = RequestContext(request,
                {
                    'jumplink_content': jumplink_content,
                    'login_content': login_content,
                    "art_content": articles_content, # legacy usage in templates
                    "articles_content": articles_content,
                    "articles_list": articles_list,
                    "jobs_content": jobs_content,
                    "jobs_list": jobs_list,
                    "news_content": news_content,
                    "news_list": news_list,
                    "pages_content": pages_content,
                    "pages_list": pages_content,
                    "events": events_list, # legacy usage in templates
                    "events_content": events_content,
                    "events_list": events_list,
                    "events_type": events_type
                })
        content = text.render(context)

        template_name = "newsletters/content.html"
        return render_to_response(
            template_name, {
            'content': content,
            'template': template},
            context_instance=RequestContext(request))