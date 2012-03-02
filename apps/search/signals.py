from django.contrib.contenttypes.models import ContentType
from search.models import UnindexedItem

def save_unindexed_item(sender, **kwargs):
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)
    UnindexedItem.objects.get_or_create(content_type=content_type, object_id=instance.id)
