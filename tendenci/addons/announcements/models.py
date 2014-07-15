from django.contrib.contenttypes import generic
from django.db import models
from tinymce import models as tinymce_models

from tendenci.addons.announcements.managers import EmergencyAnnouncementManager
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission


class EmergencyAnnouncement(TendenciBaseModel):
    title = models.CharField(max_length=250)
    content = tinymce_models.HTMLField()
    enabled = models.BooleanField(default=True)

    perms = generic.GenericRelation(ObjectPermission,
                                    object_id_field="object_id",
                                    content_type_field="content_type")
    objects = EmergencyAnnouncementManager()

    class Meta:
        permissions = (("view_emergencyannouncement","Can view emergency announcement"),)
        verbose_name = 'Emergency Announcement'
        verbose_name_plural = 'Emergency Announcements'

    def __unicode__(self):
        return self.title
