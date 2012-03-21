from django.contrib.contenttypes.models import ContentType
from search.models import UnindexedItem

def save_unindexed_item(sender, **kwargs):
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)
    # get_or_create fails in rare cases, throwing MultipleObjectsReturned errors
    # switched to try/except to prevent errors
    try:
        UnindexedItem.objects.get(content_type=content_type, object_id=instance.id)
    except:
        UnindexedItem.objects.create(content_type=content_type, object_id=instance.id)
