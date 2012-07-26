from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.apps.projects.managers import ProjectManager
from tendenci.core.files.models import file_directory, File

class ProjectName(models.Model):
    title = models.CharField(_(u'title'), max_length=200,)

    def __unicode__(self):
        return self.title    

    
class Program(models.Model):
    title = models.CharField(_(u'title'), max_length=200,)

    def __unicode__(self):
        return self.title


class ProgramYear(models.Model):
    title = models.CharField(_(u'title'), max_length=200,)
    
    def __unicode__(self):
        return self.title


class ProjectNumber(models.Model):
    number = models.CharField(_(u'number'), max_length=200,)
    
    def __unicode__(self):
        return self.number


class RpseaPm(models.Model):
    name = models.CharField(_(u'name'), max_length=200,)
    
    def __unicode__(self):
        return self.name

 
class AccessType(models.Model):
    title = models.CharField(_(u'title'), max_length=200,)
    
    def __unicode__(self):
        return self.title


class ResearchCategory(models.Model):
    title = models.CharField(_(u'title'), max_length=200,)
    
    def __unicode__(self):
        return self.title


class Project(TendenciBaseModel):
    """
    Projects plugin comments
    """
    tags = TagField(blank=True, help_text='Tag 1, Tag 2, ...')
    title = models.CharField(_(u'title'), max_length=200,)
    slug = models.SlugField(_(u'slug'), unique=True, blank=False, max_length=200, default=u'',)
    project_name = models.ForeignKey(ProjectName, null=True, blank=True)
    program = models.ForeignKey(Program, null=True, blank=True)
    program_year = models.ForeignKey(ProgramYear, null=True, blank=True)
    project_number = models.ForeignKey(ProjectNumber, null=True, blank=True)
    project_status = models.CharField(_(u'project status'), max_length=200,
        choices=(('active','active'),('completed','completed'),
                 ('selected awaiting funding','selected awaiting funding'),))
    principal_investigator = models.CharField(_(u'principal investigator'), max_length=200,)
    principal_investigator_company = models.CharField(_(u'principal investigator company'), max_length=200,)
    participants = models.CharField(_(u'participants'), max_length=200,)
    rpsea_pm = models.ForeignKey(RpseaPm, null=True, blank=True)
    start_dt = models.DateTimeField(_(u'start date'),)
    end_dt = models.DateTimeField(_(u'end date'),)
    project_abstract = models.FileField(_(u'project abstract'), upload_to=file_directory)
    project_abstract_date = models.DateTimeField(_(u'project abstract date'),)
    project_fact_sheet_title = models.CharField(_(u'project fact sheet title'), max_length=200,)
    project_fact_sheet_url = models.URLField(_(u'project fact sheet url'), max_length=200,)
    website_title = models.CharField(_(u'website title'), max_length=200,)
    website_url = models.URLField(_(u'website url'), max_length=200,)
    article_title = models.CharField(_(u'article title'), max_length=200,)
    article_url = models.URLField(_(u'article url'), max_length=200,)
    project_objectives = models.TextField(_(u'project objectives'),)
    video_embed_code = models.TextField(_(u'video embed code'),)
    video_title = models.CharField(_(u'video_title'), max_length=200,)
    video_description = models.TextField(_(u'video description'),)
    access_type = models.ForeignKey(AccessType, null=True, blank=True)
    research_category = models.ForeignKey(ResearchCategory, null=True, blank=True)
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = ProjectManager()
    
    def __unicode__(self):
        return unicode(self.id)
    
    class Meta:
        permissions = (("view_project","Can view project"),)
    
    @models.permalink
    def get_absolute_url(self):
        return ("projects.detail", [self.slug])
    
    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)


class Presentation(File):
    project = models.ForeignKey(Project, related_name="%(app_label)s_%(class)s_related")
    title = models.CharField(_(u'title'), max_length=200,)
    presentation_dt = models.DateTimeField(_(u'presentation date'),)
    
    def __unicode__(self):
        return self.title


class Report(File):
    project = models.ForeignKey(Project, related_name="%(app_label)s_%(class)s_related")
    type = models.CharField(_(u'text'), max_length=200,)
    other = models.CharField(_(u'other'), max_length=200,)
    report_dt = models.DateTimeField(_(u'report date'),)
    
    def __unicode__(self):
        return self.type


class Article(File):
    project = models.ForeignKey(Project, related_name="%(app_label)s_%(class)s_related")
    article_dt = models.DateTimeField(_(u'article date'),)
    

class Picture(File):
    project = models.ForeignKey(Project, related_name="%(app_label)s_%(class)s_related")
