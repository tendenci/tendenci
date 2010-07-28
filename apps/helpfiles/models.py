import uuid

from django.db import models

from perms.models import TendenciBaseModel 
from entities.models import Entity

class HelpFiles(TendenciBaseModel):
    guid = models.CharField(max_length=40, default=uuid.uuid1)
    entity = models.ForeignKey(Entity, null=True)
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    view_totals = models.IntegerField(default=0)
    faq = models.BooleanField(null=True, blank=True)
    featured = models.BooleanField(null=True, blank=True)

    # TODO: figure out nicer way to do this
    basic = models.BooleanField(null=True, blank=True)
    intermediate = models.BooleanField(null=True, blank=True)
    advanced = models.BooleanField(null=True, blank=True)
    expert = models.BooleanField(null=True, blank=True)

    video_included = models.BooleanField(null=True, blank=True)
    syndicate = models.BooleanField(null=True, blank=True)
    topics = models.ManyToManyField('HelpTopics')

class HelpTopics(TendenciBaseModel):
    guid = models.CharField(max_length=40, default=uuid.uuid1)
    title = models.CharField(max_length=50, blank=True)
    content = models.TextField(blank=True)