import uuid
from django.db import models, connection
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.models import User, Permission
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.utils import IntegrityError

from tendenci.core.base.fields import SlugField
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.apps.user_groups.managers import GroupManager


class Group(TendenciBaseModel):
    name = models.CharField(_('Group Name'), max_length=255, unique=True)
    slug = SlugField(_('URL Path'), unique=True)
    guid = models.CharField(max_length=40)
    label = models.CharField(_('Group Label'), max_length=255, blank=True)
    type = models.CharField(max_length=75, blank=True, choices=(
                                                             ('distribution', 'Distribution'),
                                                             ('security', 'Security'),), default='distribution')
    email_recipient = models.CharField(_('Recipient Email'), max_length=255, blank=True)
    show_as_option = models.BooleanField(_('Display Option'), default=1, blank=True)
    allow_self_add = models.BooleanField(_('Allow Self Add'), default=1)
    allow_self_remove = models.BooleanField(_('Allow Self Remove'), default=1)
    sync_newsletters = models.BooleanField(_('Sync for newsletters'), default=1)
    description = models.TextField(blank=True)
    auto_respond = models.BooleanField(_('Auto Responder'), default=0)
    auto_respond_priority = models.FloatField(_('Priority'), blank=True, default=0)
    notes = models.TextField(blank=True)
    members = models.ManyToManyField(User, through='GroupMembership')

    group = models.OneToOneField(AuthGroup, null=True, default=None, on_delete=models.SET_NULL)
    permissions = models.ManyToManyField(Permission, related_name='group_permissions', blank=True)
    # use_for_membership = models.BooleanField(_('User for Membership Only'), default=0, blank=True)

    objects = GroupManager()

    class Meta:
        permissions = (("view_group", "Can view group"),)
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        ordering = ("name",)

    def __unicode__(self):
        return self.label or self.name

    @models.permalink
    def get_absolute_url(self):
        return ('group.detail', [self.slug])

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not self.guid:
            self.guid = uuid.uuid1()

        if not self.slug:
            self.slug = slugify(self.name)

        if self.name and not self.group:
            try:
                group = AuthGroup.objects.create(name=self.name)
            except IntegrityError:
                connection._rollback()
                id = AuthGroup.objects.count()
                group = AuthGroup.objects.create(name=" ".join([self.name, str(id)]))
            group.save()
            self.group = group

        elif self.name and self.group:
            self.group.name = self.name
            try:
                self.group.save()
            except IntegrityError:
                connection._rollback()

        super(Group, self).save(force_insert, force_update, *args, **kwargs)
     
    @property    
    def active_members(self):
        return GroupMembership.objects.filter(
                                            group=self,
                                            status=True, 
                                            status_detail='active')

    def is_member(self, user):
        # impersonation
        user = getattr(user, 'impersonated_user', user)
        return user in self.members.all()

    def add_user(self, user, **kwargs):
        """
        add a user to the group; check for duplicates
        return (user, created)
        """
        from django.db import IntegrityError
        from django.db import transaction, connection

        try:
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
            return user, True  # created
        except IntegrityError:
            connection._rollback()
            return user, False
        except Exception:
            transaction.rollback()
            return user, False


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

    @classmethod
    def add_to_group(cls, **kwargs):
        """
        Easily add someone to a group, we're setting basic defaults
        e.g. GroupMembership.add_to_group(member=member, group=group)
        """
        member = kwargs['member']
        group = kwargs['group']
        editor = kwargs.get('editor', member)
        status = kwargs.get('status', True)
        status_detail = kwargs.get('status_detail', 'active')

        return cls.objects.create(
            group=group,
            member=member,
            creator_id=editor.pk,
            creator_username=editor.username,
            owner_id=editor.pk,
            owner_username=editor.username,
            status=status,
            status_detail=status_detail
        )
