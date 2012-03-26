from django.db.models import signals
from haystack import indexes
from haystack import site

from recurring_payments.models import RecurringPayment

class RecurringPaymentIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='user', faceted=True)
    user_object = indexes.CharField(model_attr='user', faceted=True)
    description = indexes.CharField(model_attr='description')
    payment_amount = indexes.FloatField(model_attr='payment_amount')   

    def get_updated_field(self):
        return 'update_dt'

    def prepare_user_object(self, obj):
        return obj.user.username

    def prepare_user(self, obj):
        return "%s" % (
            obj.user.get_full_name,
        )
        
    def index_queryset(self):
        return RecurringPayment.objects.all().order_by('user')

    def _setup_save(self, model):
        from search.signals import save_unindexed_item
        signals.post_save.connect(save_unindexed_item, sender=model, weak=False)
        
    def _teardown_save(self, model):
        from search.signals import save_unindexed_item
        signals.post_save.disconnect(save_unindexed_item, sender=model)

    def _setup_delete(self, obj):
        from search.signals import save_unindexed_item
        signals.post_delete.connect(self.remove_object, sender=obj)

    def _teardown_delete(self, obj):
        from search.signals import save_unindexed_item
        signals.post_delete.disconnect(self.remove_object, sender=obj)

site.register(RecurringPayment, RecurringPaymentIndex)