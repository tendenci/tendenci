from django.contrib.contenttypes.models import ContentType
from search.models import UnindexedItem

def save_unindexed_item(sender, **kwargs):
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)

    unindexed_item = UnindexedItem()
    unindexed_item.content_type = content_type
    unindexed_item.object_id = instance.id

    unindexed_item.save()
