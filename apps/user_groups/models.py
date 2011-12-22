import uuid
from django.db import models
from django.contrib.auth.models import User, Permission
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from base.fields import SlugField
from perms.models import TendenciBaseModel
from entities.models import Entity
from files.models import File

from user_groups.managers import GroupManager

class Group(TendenciBaseModel):
    name = models.CharField(_('Group Name'), max_length=255, unique=True)
    slug = SlugField(_('URL Path'), unique=True) 
    guid = models.CharField(max_length=40)
    label = models.CharField(_('Group Label'), max_length=255, blank=True)
    entity = models.ForeignKey(Entity, null=True, blank=True)
    type = models.CharField(max_length=75, blank=True, choices=(
                                                             ('distribution','Distribution'),
                                                             ('security','Security'),), default='distribution')
    email_recipient = models.CharField(_('Recipient Email'), max_length=255, blank=True)
    show_as_option = models.BooleanField(_('Display Option'), default=1, blank=True)
    allow_self_add = models.BooleanField(_('Allow Self Add'), default=1)
    allow_self_remove = models.BooleanField(_('Allow Self Remove'), default=1)
    description = models.TextField(blank=True)
    auto_respond = models.BooleanField(_('Auto Responder'), default=0)
    auto_respond_template =  models.CharField(_('Auto Responder Template'), 
        help_text=_("Auto Responder Template URL"), max_length=100, blank=True)
    auto_respond_priority = models.FloatField(_('Priority'), blank=True, default=0)
    notes = models.TextField(blank=True)
    members = models.ManyToManyField(User, through='GroupMembership')
    permissions = models.ManyToManyField(Permission, related_name='group_permissions', blank=True)
    # use_for_membership = models.BooleanField(_('User for Membership Only'), default=0, blank=True)
    
    objects = GroupManager()

    class Meta:
        permissions = (("view_group","Can view group"),)
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        
            
    def __unicode__(self):
        return self.label or self.name

    @models.permalink
    def get_absolute_url(self):
        return ('group.detail', [self.slug])

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            name = self.name
            self.guid = uuid.uuid1()
            if not self.slug:
                self.slug = slugify(name)
            
        super(Group, self).save(force_insert, force_update)

    def is_member(self, user):
        # impersonation
        user = getattr(user, 'impersonated_user', user)
        return user in self.members.all()

    def add_user(self, user, **kwargs):
        """
        add a user to the group; check for duplicates
        return (user, created)
        """

        # check if user in group
        in_group = GroupMembership.objects.filter(group=self, member=user).exists()
        if in_group: return (user, False)  # user, created

        # if user not in group; insert into group
        GroupMembership.objects.create(**{
            'group': self,
            'member': user,
            'creator_id': kwargs.get('creator_id') or user.pk,
            'creator_username': kwargs.get('creator_username') or user.username,
            'owner_id': kwargs.get('owner_id') or user.pk,
            'owner_username': kwargs.get('owner_username') or user.username,
            'status': kwargs.get('status') or True,
            'status_detail': kwargs.get('status_detail') or 'active',
        })

        return (user, True)  # user, created

class GroupMembership(models.Model):
    group = models.ForeignKey(Group)
    member = models.ForeignKey(User, related_name='group_member')
    
    role = models.CharField(max_length=255, default="", blank=True)
    sort_order =  models.IntegerField(_('Sort Order'), default=0, blank=True)

    # the reason this model doesn't inherit from TendenciBaseModel is
    # because it cannot have more than two foreignKeys on User
    # http://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    creator_id = models.IntegerField(default=0, editable=False)
    creator_username = models.CharField(max_length=50, editable=False)
    owner_id = models.IntegerField(default=0, editable=False)
    owner_username = models.CharField(max_length=50, editable=False)
    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50, choices=(
        ('active','Active'), ('inactive','Inactive'),), default='active')
    
    create_dt = models.DateTimeField(auto_now_add=True, editable=False)
    update_dt = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.group.name
    
    class Meta:
        unique_together = ('group', 'member',)
        verbose_name = "Group Membership"
        verbose_name_plural = "Group Memberships"

class ImportFile(File):
    group = models.ForeignKey(Group)
    
    def __unicode__(self):
        return "%s" % self.group.name
