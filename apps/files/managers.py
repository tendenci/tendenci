from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager
from haystack.query import SearchQuerySet

class FileManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses Haystack to query. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        
        if query: 
            sqs = sqs.auto_query(sqs.query.clean(query))
        else:
            sqs = sqs.all()

        sqs = sqs.order_by('-update_dt')
        
        return sqs.models(self.model)

    def get_for_model(self, instance):
        return self.model.objects.filter(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
        )