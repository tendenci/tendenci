from django.db.models import signals

from haystack import indexes
from haystack import site

from search.signals import save_unindexed_item
from invoices.models import Invoice

class InvoiceIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    object_type = indexes.CharField(model_attr='object_type', null=True)
    object_id = indexes.IntegerField(model_attr='object_id', null=True)
    bill_to = indexes.CharField(model_attr='bill_to')
    bill_to_first_name = indexes.CharField(model_attr='bill_to_first_name', default='')
    bill_to_last_name = indexes.CharField(model_attr='bill_to_last_name', default='')
    bill_to_company = indexes.CharField(model_attr='bill_to_company', default='')
    bill_to_address = indexes.CharField(model_attr='bill_to_address', default='')
    bill_to_city = indexes.CharField(model_attr='bill_to_city', default='')
    bill_to_state = indexes.CharField(model_attr='bill_to_state', default='')
    bill_to_zip_code = indexes.CharField(model_attr='bill_to_zip_code', default='')
    bill_to_country = indexes.CharField(model_attr='bill_to_country', default='')
    bill_to_phone = indexes.CharField(model_attr='bill_to_phone', default='')
    bill_to_email = indexes.CharField(model_attr='bill_to_email', default='')
    total = indexes.FloatField(model_attr='total')
    balance = indexes.FloatField(model_attr='balance')

    create_dt = indexes.DateTimeField(model_attr='create_dt')
    creator = indexes.CharField(model_attr='creator', null=True)
    creator_username = indexes.CharField(model_attr='creator_username', default='')
    owner = indexes.CharField(model_attr='owner', null=True)
    owner_username = indexes.CharField(model_attr='owner_username', default='')
    status = indexes.BooleanField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'

    def prepare_object_type(self, obj):
        myobj = obj.get_object()
        if myobj:
            return myobj._meta.verbose_name
        return obj.object_type

    def _setup_save(self, model):
        signals.post_save.connect(save_unindexed_item, sender=model, weak=False)
        
    def _teardown_save(self, model):
        signals.post_save.disconnect(save_unindexed_item, sender=model)

    def _setup_delete(self, obj):
        signals.post_delete.connect(self.remove_object, sender=obj)

    def _teardown_delete(self, obj):
        signals.post_delete.disconnect(self.remove_object, sender=obj)

site.register(Invoice, InvoiceIndex)
