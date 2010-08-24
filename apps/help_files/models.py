from django.db import models
from django.utils.translation import ugettext_lazy as _

from entities.models import Entity
from perms.models import TendenciBaseModel
from tinymce import models as tinymce_models
from managers import HelpFileManager

class Topic(models.Model):
    """Help topic"""
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

class HelpFile(TendenciBaseModel):
    """Question/Answer infromation"""
    LEVELS = ('basic', 'intermediate', 'advanced', 'expert')
    LEVEL_CHOICES = [(i,i) for i in LEVELS]
    
    topics = models.ManyToManyField(Topic)
    entity = models.ForeignKey(Entity, null=True, blank=True)
    question = models.CharField(max_length=500)
    answer = tinymce_models.HTMLField()
    level = models.CharField(choices=LEVEL_CHOICES, max_length=100, default='basic')
    is_faq = models.BooleanField()
    is_featured = models.BooleanField()
    is_video = models.BooleanField()
    syndicate = models.BooleanField(_('Include in RSS feed'),)
    view_totals = models.PositiveIntegerField(default=0)
    
    objects = HelpFileManager()

    class Meta:
        permissions = (("view_helpfile","Can view help file"),)

    @models.permalink
    def get_absolute_url(self):
        return ("help_file.details", [self.pk])
                
    def __unicode__(self):
        return self.question
    
    def level_is(self):
        "Template helper: {% if file.level_is.basic %}..."
        return dict([i, self.level==i] for i in HelpFile.LEVELS)

class Request(models.Model):
    question = models.TextField()
    
    def __unicode__(self):
        return self.question