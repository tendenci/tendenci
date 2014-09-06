import operator

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User

from haystack.query import SearchQuerySet

class RecurringPaymentManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """Recurring payment haystack search.
            Returns a SearchQuerySet
        """
        from tendenci.apps.recurring_payments.models import RecurringPayment
        sqs = SearchQuerySet()

        if query:
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()

        return sqs.models(RecurringPayment)
