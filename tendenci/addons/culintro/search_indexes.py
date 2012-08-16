from haystack import indexes
from haystack import site

from tendenci.addons.jobs.search_indexes import JobIndex
from tendenci.addons.culintro.models import CulintroJob

class CulintroJobIndex(JobIndex):
    text = indexes.CharField(document=True, use_template=True)
    open_call = indexes.BooleanField(model_attr='open_call')
    slug = indexes.CharField(model_attr='slug')
    location_2 = indexes.CharField(model_attr='location_2')

site.register(CulintroJob, CulintroJobIndex)
