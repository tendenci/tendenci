from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.apps.chamberlin_projects.managers import ProjectManager


class ConstructionType(models.Model):
    name = models.CharField(_(u'name'), max_length=200,)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name = 'Construction Type'
        verbose_name_plural = 'Construction Types'


class ConstructionActivity(models.Model):
    name = models.CharField(_(u'name'), max_length=200,)

    class Meta:
        verbose_name = 'Construction Activity'
        verbose_name_plural = 'Construction Activities'

    def __unicode__(self):
        return unicode(self.name)

class ConstructionCategory(models.Model):
    name = models.CharField(_(u'Name'), max_length=200,)
    slug = models.SlugField(_(u'Slug'), max_length=200,)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    @models.permalink
    def get_absolute_url(self):
        return ("chamberlin_projects.category", [self.slug])

class Project(TendenciBaseModel):
    """
    Projects plugin for Chamberlin
    """
    title = models.CharField(_(u'Title'), max_length=200,)
    slug = models.SlugField(_(u'Slug'), max_length=200,)
    location = models.CharField(_(u'Location'), max_length=200, blank=True,)
    city = models.CharField(_(u'City'), max_length=200, blank=True,)
    state = models.CharField(_(u'State'), max_length=200, blank=True,)
    construction_type = models.ForeignKey(ConstructionType)
    construction_activity = models.ForeignKey(ConstructionActivity)
    category = models.ForeignKey(ConstructionCategory)
    contract_amount = models.IntegerField(_(u'Contract Amount'), help_text=u'Enter a number in Dollars', null=True, blank=True,)
    owner_name = models.CharField(_(u'Owner Name'), max_length=200, blank=True,)
    architect = models.CharField(_(u'Architect'), max_length=200, blank=True,)
    general_contractor = models.CharField(_(u'General Contractor'), max_length=200, blank=True,)
    scope_of_work = models.TextField(_(u'Scope of Work'), blank=True,)
    project_description = models.TextField(_(u'Project Description'), blank=True,)
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = ProjectManager()
    
    def __unicode__(self):
        return unicode(self.title)
    
    class Meta:
        permissions = (("view_project","Can view project"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("chamberlin_projects.detail", [self.category.slug, self.slug])
