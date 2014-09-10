import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.entities.managers import EntityManager


class Entity(models.Model):
    guid = models.CharField(max_length=40)
    entity_name = models.CharField(_('Name'), max_length=200, blank=True)
    entity_type = models.CharField(_('Type'), max_length=200, blank=True)
    #entity_parent_id = models.IntegerField(_('Parent ID'), default=0)
    entity_parent = models.ForeignKey('self', related_name='entity_children', null=True, blank=True)
    # contact info
    contact_name = models.CharField(_('Contact Name'), max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)
    summary = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)

    # Model removed from TendenciBaseModel. Those fields added below
    allow_anonymous_view = models.BooleanField(_("Public can view"), default=True)
    allow_user_view = models.BooleanField(_("Signed in user can view"))
    allow_member_view = models.BooleanField()
    allow_anonymous_edit = models.BooleanField()
    allow_user_edit = models.BooleanField(_("Signed in user can change"))
    allow_member_edit = models.BooleanField()

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="%(class)s_creator", editable=False, null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name="%(class)s_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField(_("Active"), default=True)
    status_detail = models.CharField(max_length=50, default='active')

    objects = EntityManager()

    class Meta:
        permissions = (("view_entity",_("Can view entity")),)
        verbose_name_plural = _("entities")
        ordering = ("entity_name",)

    def __unicode__(self):
        return self.entity_name

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid1())

        super(Entity, self).save(*args, **kwargs)
