from django.conf import settings
from django.db import models

from tendenci.core.files.models import file_directory
from tendenci.core.newsletters.utils import extract_files
from tendenci.libs.boto_s3.utils import set_s3_file_permission


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
        permissions = (("view_newslettertemplate", "Can view newsletter template"),)

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
