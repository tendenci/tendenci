from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser

from tendenci.apps.contributions.models import Contribution


def save_contribution(sender, **kwargs):
    instance = kwargs['instance']

    if not hasattr(instance, 'owner') or not hasattr(instance, 'creator'):
        return None
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
