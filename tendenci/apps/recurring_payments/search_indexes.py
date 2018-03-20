from haystack import indexes

from tendenci.apps.recurring_payments.models import RecurringPayment
from tendenci.apps.search.indexes import CustomSearchIndex

class RecurringPaymentIndex(CustomSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='user', faceted=True)
    user_object = indexes.CharField(model_attr='user', faceted=True)
    description = indexes.CharField(model_attr='description')
    payment_amount = indexes.FloatField(model_attr='payment_amount')

    order = indexes.DateTimeField()

    def get_model(self):
        return RecurringPayment

    def get_updated_field(self):
        return 'update_dt'

    def prepare_user_object(self, obj):
        return obj.user.username

    def prepare_user(self, obj):
        return "%s" % (
            obj.user.get_full_name,
        )

    def prepare_order(self, obj):
        return obj.create_dt

    def index_queryset(self, using=None):
        return self.get_model()._default_manager.all().order_by('user')
