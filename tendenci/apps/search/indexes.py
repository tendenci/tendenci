from haystack import indexes

from django.db.models import signals

from tendenci.apps.search.signals import save_unindexed_item

class CustomSearchIndex(indexes.SearchIndex):
    """
    A custom SearchIndex subclass that saves the objects to the UnindexedItem table
    (if not already added) for later processing and deletes objects immediately.

    This requires a script to run the management command "process_unindexed" in the
    background to update index.
    """

    def _setup_save(self, model):
        signals.post_save.connect(save_unindexed_item, sender=model, weak=False)

    def _teardown_save(self, model):
        signals.post_save.disconnect(save_unindexed_item, sender=model)

    def _setup_delete(self, obj):
        signals.post_delete.connect(self.remove_object, sender=obj)

    def _teardown_delete(self, obj):
        signals.post_delete.disconnect(self.remove_object, sender=obj)