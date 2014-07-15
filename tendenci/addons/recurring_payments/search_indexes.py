from django.db.models import signals
from haystack import indexes
from haystack import site
from tendenci.addons.recurring_payments.models import RecurringPayment
from tendenci.apps.search.indexes import CustomSearchIndex

class RecurringPaymentIndex(CustomSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='user', faceted=True)
    user_object = indexes.CharField(model_attr='user', faceted=True)
    description = indexes.CharField(model_attr='description')
    payment_amount = indexes.FloatField(model_attr='payment_amount')

    order = indexes.DateTimeField()

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

    def index_queryset(self):
        return RecurringPayment.objects.all().order_by('user')


site.register(RecurringPayment, RecurringPaymentIndex)