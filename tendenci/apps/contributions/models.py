import uuid
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from django.db.models.signals import post_save

from tendenci.apps.contributions.managers import ContributionManager
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.pages.models import Page
from tendenci.apps.stories.models import Story
from tendenci.apps.files.models import File

class Contribution(TendenciBaseModel):
    guid = models.CharField(max_length=40)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    title = models.CharField(max_length=500, blank=True)

    objects = ContributionManager()

    def object(self):
        content_type = ContentType.objects.get(id=self.content_type.pk)
        object = content_type.get_object_for_this_type(id=self.object_id)
        return object

    class Meta:
#         permissions = (("view_contribution",_("Can view contribution")),)
        app_label = 'contributions'

    def get_absolute_url(self):
        return reverse('contribution', args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())

        super(Contribution, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


def save_contribution(sender, **kwargs):
    instance = kwargs['instance']

    # TODO: Possibly allow anonymous contributions
    # to be added to the system
    if isinstance(instance.owner, AnonymousUser):
        return None
    if isinstance(instance.creator, AnonymousUser):
        return None
    if not instance.owner or not instance.creator:
        return None

    content_type = ContentType.objects.get_for_model(instance)

    try:  # record exists
        contrib = Contribution.objects.get(
            content_type=content_type,
            object_id=instance.pk
            )
    except:  # create record
        contrib = Contribution()
        contrib.content_type = content_type
        contrib.object_id = instance.id
        contrib.creator = instance.owner

        title_attrs = (
            'title',
            'headline',
            'name',
        )
        for attr in title_attrs:
            if hasattr(instance, attr):
                contrib.title = getattr(instance, attr, '')
                break

        contrib.owner = instance.owner
        contrib.save()

post_save.connect(save_contribution, sender=Page, weak=False)
post_save.connect(save_contribution, sender=Story, weak=False)
post_save.connect(save_contribution, sender=File, weak=False)
