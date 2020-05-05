import datetime
import subprocess
import uuid
import re

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify

from tendenci.libs.utils import python_executable
from tendenci.apps.articles.models import Article
from tendenci.apps.emails.models import Email
from tendenci.apps.files.models import file_directory
from tendenci.apps.newsletters.utils import extract_files
from tendenci.libs.boto_s3.utils import set_s3_file_permission
from tendenci.apps.site_settings.utils import get_setting

from tendenci.apps.newsletters.utils import (
    newsletter_articles_list,
    newsletter_jobs_list,
    newsletter_news_list,
    newsletter_pages_list,
    newsletter_events_list,
    newsletter_directories_list,
    newsletter_resumes_list)

from tendenci.apps.user_groups.models import Group, GroupMembership


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

ACTIONTYPE_CHOICES = (
    ('Distribution E-mail', _('Distribution E-mail')),
    ('Direct Mail Letter', _('Direct Mail Letter')),
    ('Phone Call', _('Phone Call')),
    ('Press Release', _('Press Release')),
    ('Direct Mail Post Card', _('Direct Mail Post Card')),
    ('Newspaper Advertisement', _('Newspaper Advertisement')),
    ('Favorable Newspaper Article', _('Favorable Newspaper Article')),
    ('Unfavorable Newspaper Article', _('Unfavorable Newspaper Article'))
)

NEWSLETTER_SEND_STATUS_CHOICES = (
    ('draft', _('Draft')),
    ('queued', _('Queued')),
    ('sending', _('Sending')),
    ('sent', _('Sent')),
    ('resending', _('Resending')),
    ('resent', _('Resent'))
)


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

#     class Meta:
#         permissions = (("view_newslettertemplate", _("Can view newsletter template")),)

    def __str__(self):
        return self.name or "No Name"

    @property
    def content_type(self):
        return 'newslettertemplate'

    def get_absolute_url(self):
        return reverse('newsletter.template_render', args=[self.template_id])

    @classmethod
    def get_content_type(cls):
        from django.contrib.contenttypes.models import ContentType
        return ContentType.objects.get(
            app_label=cls._meta.app_label,
            model=cls._meta.model_name)

    def get_content_url(self):
        return reverse('newsletter.template_content', args=[self.template_id])

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
    email = models.ForeignKey(Email, null=True, on_delete=models.CASCADE)

    subject = models.CharField(max_length=255, null=True, blank=True)
    actiontype = models.CharField(max_length=30, choices=ACTIONTYPE_CHOICES, default='Distribution E-mail')
    actionname = models.CharField(max_length=255, null=True, blank=True)

    # recipient, subject fields
    member_only = models.BooleanField(default=False)
    send_to_email2 = models.BooleanField(default=False)
    group = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL, blank=True)
    include_login = models.BooleanField()
    personalize_subject_first_name = models.BooleanField()
    personalize_subject_last_name = models.BooleanField()

    # module content
    jump_links = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    events = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    event_start_dt = models.DateField()
    event_end_dt = models.DateField()
    events_type = models.IntegerField(default=1, null=True, blank=True)
    articles = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    articles_days = models.IntegerField(default=60, choices=DAYS_CHOICES)
    news = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    news_days = models.IntegerField(default=30, choices=DAYS_CHOICES)
    jobs = models.IntegerField(default=1, choices=INCLUDE_CHOICES)
    jobs_days = models.IntegerField(default=30, choices=DAYS_CHOICES)
    pages = models.IntegerField(default=0, choices=INCLUDE_CHOICES)
    pages_days = models.IntegerField(default=7, choices=DAYS_CHOICES)
    directories = models.IntegerField(default=0, choices=INCLUDE_CHOICES)
    directories_days = models.IntegerField(default=7, choices=DAYS_CHOICES)
    resumes = models.IntegerField(default=0, choices=INCLUDE_CHOICES)
    resumes_days = models.IntegerField(default=7, choices=DAYS_CHOICES)

    # default template
    default_template = models.CharField(max_length=255, null=True)

    # format
    format = models.IntegerField(default=0, choices=FORMAT_CHOICES)

    # accept software license agreement
    sla = models.BooleanField(default=False)

    # field pointing to the article if created on send
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.SET_NULL)

    # indicate the send status of the newsletter
    send_status = models.CharField(
        max_length=30,
        choices=NEWSLETTER_SEND_STATUS_CHOICES,
        default='draft')

    # important dates
    date_created = models.DateTimeField(null=True, blank=True)
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_email_sent = models.DateTimeField(null=True, blank=True)
    date_last_resent = models.DateTimeField(null=True, blank=True)

    # number of emails sent
    email_sent_count = models.IntegerField(null=True, blank=True, default=0)

    # resend_count
    resend_count = models.IntegerField(null=True, blank=True, default=0)

    # security_key will allow any user to view this newsletter from the browser
    # without logging in.
    security_key = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
#         permissions = (("view_newsletter", _("Can view newsletter")),)
        verbose_name = _("Newsletter")
        verbose_name_plural = _("Newsletters")

    def __str__(self):
        return self.actionname or "No Action Name"

    def get_absolute_url(self):
        return reverse('newsletter.detail.view', args=[self.pk])

    def generate_newsletter(self, request, template):
        if self.default_template:
            content = self.generate_from_default_template(request, template)
            return content

        return ''

    def clone(self):
        """
        Clone this newsletter and return the cloned newsletter.
        """
        ignore_fields = [
            'id',
            'email',
            'send_status',
            'date_created',
            'date_email_sent',
            'date_last_resent',
            'email_sent_count',
            'resend_count',
            'security_key'
        ]
        field_names = [field.name
            for field in self.__class__._meta.fields
            if field.name not in ignore_fields
        ]

        newsletter_new = self.__class__()
        for name in field_names:
            if hasattr(self, name):
                setattr(newsletter_new, name, getattr(self, name))
        newsletter_new.date_created = datetime.datetime.now()
        newsletter_new.subject = '(Cloned) {}'.format(self.subject)
        newsletter_new.actionname = newsletter_new.subject

        # copy email - don't link the cloned newsletter to the same email
        if self.email:
            email_ignore_fields = [
                'id',
            ]
            email_field_names = [field.name
                for field in self.email.__class__._meta.fields
                if field.name not in email_ignore_fields
            ]
            email_new = self.email.__class__()
            for name in email_field_names:
                if hasattr(self.email, name):
                    setattr(email_new, name, getattr(self.email, name))
            email_new.save()

            newsletter_new.email = email_new

        newsletter_new.save()

        return newsletter_new

    def generate_from_default_template(self, request, template):
        data = self.generate_newsletter_contents(request)
        content = template

        if '[menu]' in content:
            content = content.replace('[menu]', data.get('jumplink_content'))

        if '[content]' in content:
            full_content = data.get('opening_text') + \
                           data.get('login_content')

            content = content.replace('[content]', full_content)

        if '[articles]' in content:
            content = content.replace('[articles]', data.get('articles_content'))

        if '[releases]' in content:
            content = content.replace('[releases]', data.get('news_content'))

        if '[calendarevents]' in content:
            content = content.replace('[calendarevents]', data.get('events_content'))

        if '[jobs]' in content:
            content = content.replace('[jobs]', data.get('jobs_content'))

        if '[pages]' in content:
            content = content.replace('[pages]', data.get('pages_content'))

        if '[directories]' in content:
            content = content.replace('[directories]', data.get('directories_content'))

        if '[resumes]' in content:
            content = content.replace('[resumes]', data.get('resumes_content'))

        if '[footer]' in content:
            content = content.replace('[footer]', data.get('footer_text'))

        if '[unsubscribe]' in content:
            content = content.replace('[unsubscribe]', data.get('unsubscribe_text'))

        content = content.replace('[site_url]', get_setting('site', 'global', 'siteurl'))
        content = content.replace('[site_mailing_address]', get_setting('site', 'global', 'sitemailingaddress'))
        content = content.replace('[site_contact_email]', get_setting('site', 'global', 'sitecontactemail'))
        content = content.replace('[site_phone_number]', get_setting('site', 'global', 'sitephonenumber'))

        return content

    def generate_newsletter_contents(self, request):
        simplified = True if self.format == 0 else False

        opening_txt = render_to_string(template_name='newsletters/opening_text.txt',
                                            request=request)

        footer_txt = render_to_string(template_name='newsletters/footer.txt',
                                            context={'newsletter': self },
                                            request=request)

        unsubscribe_txt = render_to_string(template_name='newsletters/newsletter_unsubscribe.txt',
                                            request=request)

        view_from_browser_txt = render_to_string(template_name='newsletters/view_from_browser.txt',
                                            request=request)

        login_content = ""
        if self.include_login:
            login_content = render_to_string(template_name='newsletters/login.txt',
                                             request=request)

        jumplink_content = ""
        if self.jump_links:
            jumplink_content = render_to_string(template_name='newsletters/jumplinks.txt', context=locals(),
                                                request=request)

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

        directories_content = ""
        directories_list = []
        if self.directories:
            directories_list, directories_content = newsletter_directories_list(request, self.directories_days, simplified)

        resumes_content = ""
        resumes_list = []
        if self.resumes:
            resumes_list, resumes_content = newsletter_resumes_list(request, self.resumes_days, simplified)

        events_content = ""
        events_list = []
        events_type = self.events_type
        if self.events:
            events_list, events_content = newsletter_events_list(
                request,
                start_dt=self.event_start_dt,
                end_dt=self.event_end_dt,
                simplified=simplified)

        data = {
                'opening_text': opening_txt,
                'footer_text' : footer_txt,
                'unsubscribe_text': unsubscribe_txt,
                'browser_text': view_from_browser_txt,
                'login_content': login_content,
                'jumplink_content': jumplink_content,
                'articles_content': articles_content,
                'articles_list': articles_list,
                'news_content': news_content,
                'news_list': news_list,
                'jobs_content': jobs_content,
                'jobs_list': jobs_list,
                'pages_content': pages_content,
                'pages_list': pages_list,
                'directories_content': directories_content,
                'directories_list': directories_list,
                'resumes_content': resumes_content,
                'resumes_list': resumes_list,
                'events_list': events_list,
                'events_content': events_content,
                'events_type': events_type}

        return data

    def generate_article(self, user):
        if not self.article:
            # Newsletters retains full HTML tags like <html>, <head>, <body> ...,
            # but we only need the content within the <body> tag for the article body.
            email_body = self.email.body
            p = re.compile(r'<body[^>]*>([\d\D\s\S\w\W]*?)</body>')
            match = p.search(email_body)
            if match:
                email_body = match.group(1)

            slug = slugify(self.email.subject)
            if len(slug) > 100 or Article.objects.filter(slug=slug).exists():
                count = str(Article.objects.count())
                slug = '{0}-{1}'.format(slug[:99-len(count)], count)
            
            article = Article.objects.create(
                creator=user,
                creator_username=user.username,
                owner=user,
                owner_username=user.username,
                release_dt=datetime.datetime.now(),
                headline=self.email.subject[:200],
                slug=slug,
                body=email_body.replace('[browser_view_url]', reverse('newsletter.view_from_browser', args=[self.id])))

            self.article = article
            self.save()
            return True

        return False

    def get_recipients(self):
        """
        Method that will generate the recipients of the newsletter
        """
        from tendenci.apps.memberships.models import MembershipType
        if self.member_only:
            members = GroupMembership.objects.filter(
                status=True,
                status_detail='active',
                group_id__in=MembershipType.objects.filter(status_detail='active').values_list('group_id', flat=True),
                is_newsletter_subscribed=True).order_by(
                'member__email').distinct(
                'member__email')

        else:
            group = self.group
            members = GroupMembership.objects.filter(
                group=group,
                status=True,
                status_detail='active',
                is_newsletter_subscribed=True).order_by(
                'member__email').distinct(
                'member__email')

        return members

    def send_to_recipients(self):
        subprocess.Popen([python_executable(), "manage.py",
                              "send_newsletter",
                              str(self.pk)])

    def save(self, *args, **kwargs):
        if self.security_key == '' or self.security_key is None:
            self.security_key = uuid.uuid4()
        if self.actionname != self.subject:
            self.actionname = self.subject
        if "log" in kwargs:
            kwargs.pop('log')
        super(Newsletter, self).save(*args, **kwargs)

    def get_browser_view_url(self):
        site_url = get_setting('site', 'global', 'siteurl')
        return "%s%s?key=%s" % (site_url, reverse('newsletter.view_from_browser', args=[self.pk]), self.security_key)
