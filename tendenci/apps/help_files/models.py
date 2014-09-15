from django.db import models
from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.base.fields import SlugField
from tinymce import models as tinymce_models
from managers import HelpFileManager

class Topic(models.Model):
    """Help topic"""
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['title']

    @models.permalink
    def get_absolute_url(self):
        return ("help_files.topic", [self.pk])

    def __unicode__(self):
        return self.title

class HelpFile(TendenciBaseModel):
    """Question/Answer infromation"""
    LEVELS = ('basic', 'intermediate', 'advanced', 'expert')
    LEVEL_CHOICES = [(i,i) for i in LEVELS]

    slug = SlugField(_('URL Path'), unique=True)
    topics = models.ManyToManyField(Topic)
    question = models.CharField(max_length=500)
    answer = tinymce_models.HTMLField()
    level = models.CharField(choices=LEVEL_CHOICES, max_length=100, default='basic')
    is_faq = models.BooleanField()
    is_featured = models.BooleanField()
    is_video = models.BooleanField()
    syndicate = models.BooleanField(_('Include in RSS feed'), default=True)
    view_totals = models.PositiveIntegerField(default=0)

    group = models.ForeignKey(Group, null=True, default=get_default_group, on_delete=models.SET_NULL)
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = HelpFileManager()

    class Meta:
        permissions = (("view_helpfile",_("Can view help file")),)

    @models.permalink
    def get_absolute_url(self):
        return ("help_file.details", [self.slug])

    def __unicode__(self):
        return self.question

    def level_is(self):
        "Template helper: {% if file.level_is.basic %}..."
        return dict([i, self.level==i] for i in HelpFile.LEVELS)


class HelpFile_Topics(models.Model):
    """
    This table is created automatically by the Many To
    Many Relationship. It is added here to use in the
    views to help optimize for certain queries.
    """
    helpfile = models.ForeignKey(HelpFile)
    topic = models.ForeignKey(Topic)

    class Meta:
        managed = False

class Request(models.Model):
    question = models.TextField()

    def __unicode__(self):
        return self.question


class HelpFileMigration(models.Model):
    """
        Unmanaged model to map old tendenci 4 id
        to the new tendenci 5 id
    """
    t4_id = models.IntegerField()
    t5_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mig_help_files_helpfile_t4_to_t5'


