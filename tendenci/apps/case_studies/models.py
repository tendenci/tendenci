from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.apps.perms.object_perms import ObjectPermission
from tagging.fields import TagField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.case_studies.managers import CaseStudyManager

from tendenci.apps.files.models import File
from tendenci.apps.files.managers import FileManager


class CaseStudy(TendenciBaseModel):
    client = models.CharField(max_length=75)
    website = models.URLField(max_length=150)
    slug = models.SlugField(max_length=100)
    overview = models.TextField(blank=True, null=True)
    execution = models.TextField(blank=True, null=True)
    results = models.TextField(blank=True, null=True)
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))

    perms = GenericRelation(ObjectPermission, object_id_field="object_id", content_type_field="content_type")

    objects = CaseStudyManager()

    def __str__(self):
        return self.client

    class Meta:
#         permissions = (("view_casestudy","Can view case study"),)
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'
        app_label = 'case_studies'

    def delete(self, *args, **kwargs):
        for img in self.image_set.all():
            img.delete()
        return super(CaseStudy, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('case_study.view', args=[self.slug])

    def featured_screenshots(self):
        try:
            return self.image_set.filter(file_type='featured')
        except:
            return False

    def screenshots(self):
        try:
            return self.image_set.filter(file_type='screenshot')
        except:
            return False

    def other_images(self):
        try:
            return self.image_set.filter(file_type='other')
        except:
            return False

    def homepage_images(self):
        try:
            return self.image_set.filter(file_type='homepage')
        except:
            return False


class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        app_label = 'case_studies'

    def get_absolute_url(self):
        return reverse('case_study.service', args=[self.pk])


class Technology(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = "Technology"
        verbose_name_plural = "Technologies"
        app_label = 'case_studies'

    def get_absolute_url(self):
        return reverse('case_study.technology', args=[self.pk])


class Image(File):

    FILE_TYPE_FEATURED = 'featured'
    FILE_TYPE_SCREENSHOT = 'screenshot'
    FILE_TYPE_HOMEPAGE = 'homepage'
    FILE_TYPE_OTHER = 'other'

    FILE_TYPE_CHOICES = (
        (FILE_TYPE_FEATURED, 'Featured Screenshot'),
        (FILE_TYPE_SCREENSHOT, 'Screenshot'),
        (FILE_TYPE_HOMEPAGE, 'Homepage Image'),
        (FILE_TYPE_OTHER,'Other'),
    )

    case_study = models.ForeignKey(CaseStudy, on_delete=models.CASCADE)
    file_ptr = models.OneToOneField(File, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE, parent_link=True)
    file_type = models.CharField(
        _('File type'),
        max_length=50,
        choices=FILE_TYPE_CHOICES,
        default=FILE_TYPE_OTHER,
    )
    position = models.IntegerField(blank=True)

    objects = FileManager()

    def save(self, *args, **kwargs):
        if self.position is None:
            # Append
            try:
                last = Image.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(Image, self).save(*args, **kwargs)

    class Meta:
        ordering = ('position',)
        app_label = 'case_studies'
