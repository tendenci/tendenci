from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from managers import ArchitectureProjectManager

from files.models import File

class ArchitectureProject(TendenciBaseModel):
    project_title = models.CharField(max_length=250, blank=True, null=True)
    architect = models.CharField(max_length=250, blank=True, null=True)
    client = models.CharField(max_length=250)
    website = models.URLField(max_length=500)
    slug = models.SlugField(max_length=100, unique=True)
    url = models.URLField()
    overview = models.TextField(blank=True, null=True)
    execution = models.TextField(blank=True, null=True)
    results = models.TextField(blank=True, null=True)
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))
    categories = models.ManyToManyField('Category')
    building_types = models.ManyToManyField('BuildingType')
    ordering = models.IntegerField(blank=True, null=True)

    objects = ArchitectureProjectManager()

    def __unicode__(self):
        return self.client

    def save(self, *args, **kwargs):
        model = self.__class__
        
        if self.ordering is None:
            # Append
            try:
                last = model.objects.order_by('-ordering')[0]
                self.ordering = last.ordering + 1
            except:
                # First row
                self.ordering = 0
        
        return super(ArchitectureProject, self).save(*args, **kwargs)


    class Meta:
        permissions = (("view_architectureproject","Can view architecture project"),)
        verbose_name = 'Architecture Project'
        verbose_name_plural = 'Architecture Projects'
        ordering = ('ordering',)

    def delete(self, *args, **kwargs):
        for img in self.image_set.all():
            img.delete()
        return super(ArchitectureProject, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("architecture_project.view", [self.slug])
        
    def featured_images(self):
        try:
            return self.image_set.filter(file_type='featured')
        except:
            return False
    
    def images(self):
        try:
            return self.image_set.filter(file_type='image')
        except:
            return False
            
    def other_images(self):
        try:
            return self.image_set.filter(file_type='other')
        except:
            return False

    def sidebar_images(self):
        try:
            return self.image_set.filter(file_type='sidebar')
        except:
            return False

    def logo_images(self):
        try:
            return self.image_set.filter(file_type='logo')
        except:
            return False

class Category(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']

    @models.permalink
    def get_absolute_url(self):
        return ("architecture_project.category", [self.pk])


class BuildingType(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']
        permissions = (("view_architecture_project","Can view project"),)

    @models.permalink
    def get_absolute_url(self):
        return ("architecture_project.building_type", [self.pk])

class Image(File):
    architecture_project = models.ForeignKey(ArchitectureProject)
    file_ptr = models.OneToOneField(File, related_name="%(app_label)s_%(class)s_related")
    file_type = models.CharField(
        _('File type'),
        max_length=50,
        choices=(
            ('featured','Featured Image'),
            ('image','Image'),
            ('logo', 'Client Logo'),
            ('sidebar', 'Sidebar Image'),
            ('other','Other'),
        ),
        default='image',
    )
    position = models.IntegerField(blank=True)

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