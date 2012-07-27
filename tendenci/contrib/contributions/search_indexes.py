from haystack import indexes
from haystack import site

from tendenci.contrib.contributions.models import Contribution
from tendenci.core.perms.indexes import TendenciBaseSearchIndex


class ContributionIndex(TendenciBaseSearchIndex):
   pass

site.register(Contribution, ContributionIndex)
