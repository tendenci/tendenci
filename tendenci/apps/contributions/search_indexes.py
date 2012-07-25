from haystack import indexes
from haystack import site

from tendenci.apps.contributions.models import Contribution
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class ContributionIndex(TendenciBaseSearchIndex):
   pass

site.register(Contribution, ContributionIndex)
