import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.models import User, Permission
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.utils import IntegrityError

from tendenci.apps.base.fields import SlugField
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.user_groups.managers import GroupManager
from tendenci.apps.entities.models import Entity
from tendenci.apps.site_settings.utils import get_setting


class Group(TendenciBaseModel):

    TYPE_DISTRIBUTION = 'distribution'
    TYPE_SECURITY = 'security'
    TYPE_SYSTEM_GENERATED = 'system_generated'

    TYPE_CHOICES = (
        (TYPE_DISTRIBUTION, _('Distribution')),
        (TYPE_SECURITY, _('Security')),
        (TYPE_SYSTEM_GENERATED, _('System Generated')),
    )

    name = models.CharField(_('Group Name'), max_length=255, unique=True)
    slug = SlugField(_('URL Path'), unique=True)
    guid = models.CharField(max_length=40)
    label = models.CharField(_('Group Label'), max_length=255, blank=True)
    dashboard_url = models.CharField(_('Dashboard URL'), max_length=255, default='', blank=True,
                                     help_text=_('Enable Group Dashboard Redirect in site settings to use this feature.'))
    type = models.CharField(max_length=75, blank=True, choices=TYPE_CHOICES,
                                           default=TYPE_DISTRIBUTION)
    email_recipient = models.CharField(_('Recipient Email'), max_length=255, blank=True)
    show_as_option = models.BooleanField(_('Display Option'), default=True, blank=True)
    allow_self_add = models.BooleanField(_('Allow Self Add'), default=True)
    show_for_memberships = models.BooleanField(default=True,
            help_text=_('If checked and allows self add, this group will show as an option for the group field on membership applications'),)
    show_for_events = models.BooleanField(default=True,
            help_text=_('If checked, this group will show as an option for the group field on events'),)
    allow_self_remove = models.BooleanField(_('Allow Self Remove'), default=True)
    sync_newsletters = models.BooleanField(_('Sync for newsletters'), default=True)
    description = models.TextField(blank=True)
    auto_respond = models.BooleanField(_('Auto Responder'), default=False)
    auto_respond_priority = models.FloatField(_('Priority'), blank=True, default=0)
    notes = models.TextField(blank=True)
    members = models.ManyToManyField(User, through='GroupMembership', related_name='user_groups')

    group = models.OneToOneField(AuthGroup, null=True, default=None, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission, related_name='group_permissions', blank=True)
    # use_for_membership = models.BooleanField(_('User for Membership Only'), default=0, blank=True)

    objects = GroupManager()

    class Meta:
#         permissions = (("view_group", _("Can view group")),)
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        ordering = ("name",)
        app_label = 'user_groups'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('group.detail', args=[self.slug])

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not self.guid:
            self.guid = uuid.uuid4()

        if not self.slug:
            self.slug = slugify(self.name)

        # add the default entity
        if not self.entity:
            self.entity = Entity.objects.first()

        super(Group, self).save(force_insert, force_update, *args, **kwargs)

        if not self.group:
            # create auth group if not exists
            # note that the name of auth group is also unique
            group_name = self.get_unique_auth_group_name()
            self.group = AuthGroup.objects.create(name=group_name)
            self.save()

    @property
    def active_members(self):
        return GroupMembership.objects.filter(
            group=self, status=True, status_detail='active')

    def get_unique_auth_group_name(self):
        # get the unique name for auth group.
        # the max length of the name of the auth group is 80.
        name = self.name
        if not name:
            name = str(self.id)

        if len(name) > 80:
            name = name[:80]

        if AuthGroup.objects.filter(name=name).exists():
            name = 'User Group %d' % self.id

        return name

    def is_member(self, user):
        # impersonation
        user = getattr(user, 'impersonated_user', user)

        if isinstance(user, User):
            return self.members.filter(id=user.id).exists()

        return False

    def add_user(self, user, **kwargs):
        """
        add a user to the group; check for duplicates
        return (user, created)
        """
        if isinstance(user, User):

            # first check if user exists
            if not self.is_member(user):

                params = {
                        'group': self,
                        'member': user,
                        'creator_id': kwargs.get('creator_id') or user.pk,
                        'creator_username': kwargs.get('creator_username') or user.username,
                        'owner_id': kwargs.get('owner_id') or user.pk,
                        'owner_username': kwargs.get('owner_username') or user.username,
                        'status': kwargs.get('status') or True,
                        'status_detail': kwargs.get('status_detail') or 'active'
                        }
                try:
                    GroupMembership.objects.create(**params)
                except IntegrityError:
                    return user, False

                return user, True  # created

        return user, False

    def remove_user(self, user, **kwargs):
        if self.is_member(user):
            GroupMembership.objects.get(group=self, member=user).delete()

class GroupMembership(models.Model):

    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = (
        (STATUS_ACTIVE,  'Active'),          #TODO: Internationalisation
        (STATUS_INACTIVE, 'Inactive'),
    )

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, related_name='group_member', on_delete=models.CASCADE)

    role = models.CharField(max_length=255, default="", blank=True)
    sort_order =  models.IntegerField(_('Sort Order'), default=0, blank=True)

    # the reason this model doesn't inherit from TendenciBaseModel is
    # because it cannot have more than two foreignKeys on User
    # http://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    creator_id = models.IntegerField(default=0, editable=False)
    creator_username = models.CharField(max_length=150, editable=False)
    owner_id = models.IntegerField(default=0, editable=False)
    owner_username = models.CharField(max_length=150, editable=False)
    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50,
                                     choices=STATUS_CHOICES,
                                     default=STATUS_ACTIVE)

    create_dt = models.DateTimeField(auto_now_add=True, editable=False)
    update_dt = models.DateTimeField(auto_now=True)

    # The following fields are for Newletter Subscribe and Unsubscribe
    is_newsletter_subscribed = models.BooleanField(default=True)
    newsletter_key = models.CharField(max_length=50, null=True, blank=True) # will be the secret key for unsubscribe

    def __str__(self):
        return self.group.name

    class Meta:
        unique_together = ('group', 'member',)
        verbose_name = _("Group Membership")
        verbose_name_plural = _("Group Memberships")
        app_label = 'user_groups'

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

    def subscribe_to_newsletter(self):
        if not self.is_newsletter_subscribed:
            self.is_newsletter_subscribed = True
            # change newsletter_key when subscribing
            self.newsletter_key = uuid.uuid4()
            self.save()
            return True
        elif self.newsletter_key is None:
            self.newsletter_key = uuid.uuid4()
            self.save()
            return True
        return False

    def unsubscribe_to_newsletter(self):
        if self.is_newsletter_subscribed:
            self.is_newsletter_subscribed = False
            # change newsletter_key when unsubscribing
            self.newsletter_key = uuid.uuid4()
            self.save()
            return True

        return False

    @property
    def noninteractive_unsubscribe_url(self):
        site_url = get_setting('site', 'global', 'siteurl')
        if not self.newsletter_key:
            self.newsletter_key = uuid.uuid4()
            self.save()
        unsubscribe_path = reverse('group.newsletter_unsubscribe_noninteractive', kwargs={
            'group_slug': self.group.slug,
            'newsletter_key': self.newsletter_key
            })

        return site_url + unsubscribe_path
