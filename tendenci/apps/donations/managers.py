from django.db.models import Manager

from haystack.query import SearchQuerySet


class DonationManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
        Donations haystack to query donations.
        Returns a SearchQuerySet
        """
        from tendenci.apps.donations.models import Donation
        sqs = SearchQuerySet()

        if query:
            sqs = sqs.filter(content=sqs.query.clean(query))
        else:
            sqs = sqs.all()

        return sqs.models(Donation)
