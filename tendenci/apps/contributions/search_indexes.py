from haystack import indexes

from tendenci.apps.contributions.models import Contribution
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class ContributionIndex(TendenciBaseSearchIndex, indexes.Indexable):

    @classmethod
    def get_model(self):
        return Contribution
#
