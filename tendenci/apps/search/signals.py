from django.contrib.contenttypes.models import ContentType
from haystack import signals
from django.db import models
from django.conf import settings

from tendenci.apps.search.models import UnindexedItem
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

def save_unindexed_item(sender, **kwargs):
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)
    # get_or_create fails in rare cases, throwing MultipleObjectsReturned errors
    # switched to try/except to prevent errors

    params = {
        'content_type': content_type,
        'object_id': instance.pk
    }

    if not UnindexedItem.objects.filter(**params).exists():
        UnindexedItem.objects.create(**params)
        
        
class QueuedSignalProcessor(signals.BaseSignalProcessor):

    def get_sender_models(self):
        for app in settings.INSTALLED_APPS:
            try:
                __import__(app + '.search_indexes')
            except:
                pass
        return [c.get_model() for c in TendenciBaseSearchIndex.__subclasses__()]    
       
    def setup(self):
        # collect only those models being used for search indexes
        for model in self.get_sender_models():
            models.signals.post_save.connect(self.enqueue_save, sender=model)
            models.signals.post_delete.connect(self.handle_delete, sender=model)
 
    def teardown(self):
        for model in self.get_sender_models():
            models.signals.post_save.disconnect(self.enqueue_save, sender=model)
            models.signals.post_delete.disconnect(self.handle_delete, sender=model)
 
    def enqueue_save(self, sender, instance, **kwargs):
        kwargs.update({'instance': instance})
        save_unindexed_item(sender, **kwargs)
