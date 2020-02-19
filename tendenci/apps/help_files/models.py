from django.db import models
from django.urls import reverse
from tendenci.apps.user_groups.models import Group
from tendenci.apps.user_groups.utils import get_default_group
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.base.fields import SlugField
from tendenci.libs.tinymce import models as tinymce_models
from .managers import HelpFileManager

class Topic(models.Model):
    """Help topic"""
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['title']
        app_label = 'help_files'

    def get_absolute_url(self):
        return reverse('help_files.topic', args=[self.pk])

    def __str__(self):
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
    is_faq = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_video = models.BooleanField(default=False)
    syndicate = models.BooleanField(_('Include in RSS feed'), default=True)
    view_totals = models.PositiveIntegerField(default=0)

    group = models.ForeignKey(Group, null=True, default=get_default_group, on_delete=models.SET_NULL)
    perms = GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = HelpFileManager()

    class Meta:
#         permissions = (("view_helpfile",_("Can view help file")),)
        app_label = 'help_files'

    def get_absolute_url(self):
        return reverse('help_file.details', args=[self.slug])

    def __str__(self):
        return self.question

    def level_is(self):
        "Template helper: {% if file.level_is.basic %}..."
        return dict([i, self.level==i] for i in HelpFile.LEVELS)


class Request(models.Model):
    question = models.TextField()

    class Meta:
        app_label = 'help_files'

    def __str__(self):
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
        app_label = 'help_files'
