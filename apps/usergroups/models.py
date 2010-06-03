from django.db import models
from django.contrib.auth.models import User, Permission
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from perms.models import AuditingBaseModel
from entities.models import Entity

class Group(AuditingBaseModel):
    name = models.CharField(_('Group Name'), max_length=255, unique=True)
    slug = models.SlugField(editable=False, unique=True)
    guid = models.CharField(max_length=50, editable=False)
    label = models.CharField(_('Group Label'), max_length=255, blank=True)
    entity = models.ForeignKey(Entity, null=True, blank=True)
    type = models.CharField(max_length=75, blank=True, choices=(
                                                             ('distribution','Distribution'),
                                                             ('security','Security'),), default='distribution')
    email_recipient = models.CharField(_('Email Recipient'), max_length=255, blank=True)
    
    show_as_option = models.BooleanField(_('Display Option'), default=1)
    allow_self_add = models.BooleanField(_('Allow Self Add'), default=1)
    allow_self_remove = models.BooleanField(_('Allow Self Remove'), default=1)
    
    description = models.TextField(blank=True)
    auto_respond = models.BooleanField(_('Auto Responder'), default=0)
    auto_respond_template =  models.CharField(_('Auto Responder Template'), max_length=100, blank=True)
    auto_respond_priority = models.FloatField(_('Priority'), blank=True, default=0)
    
    notes = models.TextField(blank=True)
    
    create_dt = models.DateTimeField(auto_now_add=True)
    
    members = models.ManyToManyField(User, through='GroupMembership')
    permissions = models.ManyToManyField(Permission, related_name='group_permissions', blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('group_detail', [self.slug])

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            name = self.name
            self.slug = slugify(name)
            
        super(self.__class__, self).save(force_insert, force_update)


class GroupMembership(models.Model):
    group = models.ForeignKey(Group)
    member = models.ForeignKey(User, related_name='group_member')
    
    role = models.CharField(max_length=255, default="", blank=True)
    sort_order =  models.IntegerField(_('Sort Order'), default=0, blank=True)
    
    creator_id = models.IntegerField(default=0, editable=False)
    creator_username = models.CharField(max_length=50, editable=False)
    owner_id = models.IntegerField(default=0, editable=False)   
    owner_username = models.CharField(max_length=50, editable=False)
    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50, choices=(
                                                             ('active','Active'),
                                                             ('inactive','Inactive'),),
                                     default='active')
    
    create_dt = models.DateField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ('group', 'member',)

