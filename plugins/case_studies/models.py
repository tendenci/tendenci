from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from perms.models import TendenciBaseModel
from managers import CaseStudyManager

class CaseStudy(TendenciBaseModel):
    client = models.CharField(max_length=75)
    website = models.URLField(max_length=150)
    slug = models.SlugField(max_length=100)
    overview = models.TextField(blank=True, null=True)
    execution = models.TextField(blank=True, null=True)
    results = models.TextField(blank=True, null=True)
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))

    objects = CaseStudyManager()

    def __unicode__(self):
        return self.client

    class Meta:
        permissions = (("view_casestudy","Can view case study"),)
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'

    @models.permalink
    def get_absolute_url(self):
        return ("case_study.view", [self.slug])