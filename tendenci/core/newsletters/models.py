import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tendenci.core.files.models import file_directory
from tendenci.core.newsletters.utils import extract_files
from tendenci.libs.boto_s3.utils import set_s3_file_permission

from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group

from tinymce import models as tinymce_models


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

    # module content
    jump_links = models.IntegerField(default=1)
    events =  models.IntegerField(default=1)
    event_start_dt = models.DateField()
    event_end_dt = models.DateField()
    events_type = models.IntegerField(default=1, null=True, blank=True)
    articles = models.IntegerField(default=1)
    articles_days = models.IntegerField(default=60)
    news = models.IntegerField(default=1)
    news_days = models.IntegerField(default=30)
    jobs = models.IntegerField(default=1)
    jobs_days = models.IntegerField(default=30)
    pages = models.IntegerField(default=0)
    pages_days = models.IntegerField(default=7)

    # format
    format = models.IntegerField(default=0)