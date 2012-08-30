from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.contrib.auth.models import AnonymousUser

from tendenci.apps.contributions.models import Contribution
from tendenci.apps.pages.models import Page
from tendenci.apps.stories.models import Story
from tendenci.core.files.models import File


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
