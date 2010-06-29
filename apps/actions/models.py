import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _

from perms.models import TendenciBaseModel
from entities.models import Entity
from emails.models import Email
from user_groups.models import Group

class Action(TendenciBaseModel):
    guid = models.CharField(max_length=50, default=uuid.uuid1)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, default='Distribution E-mail')
    description = models.TextField(blank=True, null=True)
    email = models.ForeignKey(Email, blank=True, null=True)
    entity = models.ForeignKey(Entity, blank=True, null=True)
    group = models.ForeignKey(Group, blank=True, null=True)
    member_only = models.BooleanField(default=False)
    send_to_email2 = models.BooleanField(default=False)
    category = models.CharField(max_length=50)
    start_dt = models.DateTimeField(auto_now_add=True)
    finish_dt = models.DateTimeField(null=True)
    due_dt = models.DateTimeField(null=True)
    submit_dt = models.DateTimeField(null=True)
    sent = models.IntegerField(default=0)
    attempted = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    returned = models.IntegerField(default=0)
    responses = models.IntegerField(default=0)
    sla = models.BooleanField(_('Software License Agreement'), default=False)
    starting_point = models.IntegerField(default=0)
    stopping_point = models.IntegerField(default=0)
    
    @models.permalink
    def get_absolute_url(self):
        return ("action", [self.pk])

    def __unicode__(self):
        return self.name