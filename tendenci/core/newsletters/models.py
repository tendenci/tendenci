import datetime

from django.conf import settings
from django.db import models
from django.template import Template as DTemplate
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template import RequestContext

from tendenci.core.files.models import file_directory
from tendenci.core.newsletters.utils import extract_files
from tendenci.libs.boto_s3.utils import set_s3_file_permission
from tendenci.core.newsletters.utils import apply_template_media

from tendenci.core.newsletters.utils import (
    newsletter_articles_list,
    newsletter_jobs_list,
    newsletter_news_list,
    newsletter_pages_list,
    newsletter_events_list)

from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group

from tinymce import models as tinymce_models


"""
Choice constants
"""

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


class NewsletterTemplate(models.Model):
    """
    This represents a Template for Newsletters.
    """
    template_id = models.CharField(max_length=100, unique=True, null=True)
    name = models.CharField(max_length=100)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    #post only
    html_file = models.FileField(upload_to=file_directory, null=True)
    zip_file = models.FileField(upload_to=file_directory, null=True)

    class Meta:
        permissions = (("view_newslettertemplate", _("Can view newsletter template")),)

    def __unicode__(self):
        return self.name

    @property
    def content_type(self):
        return 'newslettertemplate'

    @models.permalink
    def get_absolute_url(self):
        return ("newsletter.template_render", [self.template_id])

    @classmethod
    def get_content_type(cls):
        from django.contrib.contenttypes.models import ContentType
        return ContentType.objects.get(
            app_label=cls._meta.app_label,
            model=cls._meta.module_name)

    @models.permalink
    def get_content_url(self):
        return ("newsletter.template_content", [self.template_id])

    def get_zip_url(self):
        if self.zip_file:
            return self.zip_file.url
        return ''

    def get_media_url(self):
        if self.zip_file:
            return "%snewsletters/%s" % (settings.MEDIA_URL, self.template_id)
        return ''

    def save(self, *args, **kwargs):
        super(NewsletterTemplate, self).save(*args, **kwargs)
        if self.html_file:
            set_s3_file_permission(self.html_file.file, public=True)
        if self.zip_file:
            set_s3_file_permission(self.zip_file.file, public=True)
        #extract and serve files in zip
        extract_files(self)


class Newsletter(models.Model):
    subject = models.CharField(max_length=255, null=True, blank=True)
    content = tinymce_models.HTMLField()

    # recipient, subject fields
    member_only = models.BooleanField(default=False)
    send_to_email2 = models.BooleanField(default=False)
    group = models.ForeignKey(Group, null=True, default=get_default_group, on_delete=models.SET_NULL)
    include_login = models.BooleanField()
    personalize_subject_first_name = models.BooleanField()
    personalize_subject_last_name = models.BooleanField()

    # module content
    jump_links = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    events = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    event_start_dt = models.DateField(default=datetime.date.today())
    event_end_dt = models.DateField(default=datetime.date.today()+datetime.timedelta(days=90))
    events_type = models.IntegerField(default=1, null=True, blank=True, choices=TYPE_CHOICES)
    articles = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    articles_days = models.IntegerField(default=60, choices=DAYS_CHOICES)
    news = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    news_days = models.IntegerField(default=30, choices=DAYS_CHOICES)
    jobs = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    jobs_days = models.IntegerField(default=30, choices=DAYS_CHOICES)
    pages = models.IntegerField(default=0, choices=INCLUDE_CHOICES)
    pages_days = models.IntegerField(default=7, choices=DAYS_CHOICES)

    # default template
    default_template = models.CharField(max_length=255, choices=DEFAULT_TEMPLATE_CHOICES, null=True)

    # format
    format = models.IntegerField(default=0, choices=FORMAT_CHOICES)

    def __unicode__(self):
        return self.subject

    def generate_newsletter(self, request):
        if self.default_template:
            content = self.generate_from_default_template(request)
            '[articles]' in content
            return content

        return ''
        # data = self.cleaned_data
        # subject = ''
        # subj = data.get('subject', '')
        # inc_last_name = data.get('personalize_subject_last_name')
        # inc_first_name = data.get('personalize_subject_first_name')

        # if inc_first_name and not inc_last_name:
        #     subject = '[firstname] ' + subj
        # elif inc_last_name and not inc_first_name:
        #     subject = '[lastname] ' + subj
        # elif inc_first_name and inc_last_name:
        #     subject = '[firstname] [lastname] ' + subj

        # request = self.request

        # if not has_perm(request.user, 'newsletters.view_newslettertemplate'):
        #     raise Http403



        # text = DTemplate(self.default_template)
        # context = RequestContext(request,
        #         {
        #             'jumplink_content': jumplink_content,
        #             'login_content': login_content,
        #             "art_content": articles_content, # legacy usage in templates
        #             "articles_content": articles_content,
        #             "articles_list": articles_list,
        #             "jobs_content": jobs_content,
        #             "jobs_list": jobs_list,
        #             "news_content": news_content,
        #             "news_list": news_list,
        #             "pages_content": pages_content,
        #             "pages_list": pages_content,
        #             "events": events_list, # legacy usage in templates
        #             "events_content": events_content,
        #             "events_list": events_list,
        #             "events_type": events_type
        #         })
        # content = text.render(context)

        # return content

    def generate_from_default_template(self, request):
        data = self.generate_newsletter_contents(request)
        content = self.content

        if '[menu]' in content:
            content.replace('[menu]', data.get('jumplink_content'))

        if '[content]' in content:
            full_content = data.get('login_content') + data.get('articles_content') + \
                            data.get('news_content') + data.get('jobs_content') + \
                            data.get('pages_content') + data.get('events_content')
            content.replace('[content]', full_content)

        if '[articles]' in content:
            content.replace('[articles]', data.get('articles_content'))

        if '[releases]' in content:
            content.replace('[releases]', data.get('news_content'))

        if '[calendarevents]' in content:
            content.replace('[calendarevents]', data.get('events_content'))

        if '[jobs]' in content:
            content.replace('[jobs]', data.get('jobs_content'))

        if '[pages]' in content:
            content.replace('[pages]', data.get('pages_content'))

        return content

    def generate_newsletter_contents(self, request):
        simplified = True if self.format == 0 else False
        login_content = ""
        if self.include_login:
            login_content = render_to_string('newsletters/login.txt',
                                             context_instance=RequestContext(request))

        jumplink_content = ""
        if self.jump_links:
            jumplink_content = render_to_string('newsletters/jumplinks.txt', locals(),
                                                context_instance=RequestContext(request))

        articles_content = ""
        articles_list =[]
        if self.articles:
            articles_list, articles_content = newsletter_articles_list(request, self.articles_days, simplified)

        news_content = ""
        news_list = []
        if self.news:
            news_list, news_content = newsletter_news_list(request, self.news_days, simplified)

        jobs_content = ""
        jobs_list = []
        if self.jobs:
            jobs_list, jobs_content = newsletter_jobs_list(request, self.jobs_days, simplified)

        pages_content = ""
        pages_list = []
        if self.pages:
            pages_list, pages_content = newsletter_pages_list(request, self.pages_days, simplified)

        try:
            events_type = self.events_type
            events_list, events_content = newsletter_events_list(
                request,
                start_dt=self.event_start_dt,
                end_dt=self.event_end_dt,
                simplified=simplified)

        except ImportError:
            events_list = []
            events_type = None


        return {'login_content': login_content,
                'jumplink_content': jumplink_content,
                'articles_content': articles_content,
                'articles_list': articles_list,
                'news_content': news_content,
                'news_list': news_list,
                'jobs_content': jobs_content,
                'jobs_list': jobs_list,
                'pages_content': pages_content,
                'pages_list': pages_list,
                'events_list': events_list,
                'events_content': events_content,
                'events_type': events_type }
