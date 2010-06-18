from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from contributions.managers import ContributionManager
from perms.models import AuditingBaseModel
from entities.models import Entity

class Contribution(AuditingBaseModel):

    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    title = models.CharField(max_length=500, blank=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    objects = ContributionManager()

    def object(self):
        content_type = ContentType.objects.get(id=self.content_type.pk)
        object = content_type.get_object_for_this_type(id=self.object_id)
        return object

    class Meta:
        permissions = (("view_contribution","Can view contribution"),)

    @models.permalink
    def get_absolute_url(self):
        return ("contribution", [self.pk])

    def __unicode__(self):
        return self.title