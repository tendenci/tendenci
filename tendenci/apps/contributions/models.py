import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from tendenci.apps.contributions.managers import ContributionManager
from tendenci.core.perms.models import TendenciBaseModel

class Contribution(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    title = models.CharField(max_length=500, blank=True)

    objects = ContributionManager()

    def object(self):
        content_type = ContentType.objects.get(id=self.content_type.pk)
        object = content_type.get_object_for_this_type(id=self.object_id)
        return object

    class Meta:
        permissions = (("view_contribution",_("Can view contribution")),)

    @models.permalink
    def get_absolute_url(self):
        return ("contribution", [self.pk])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())

        super(Contribution, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title
