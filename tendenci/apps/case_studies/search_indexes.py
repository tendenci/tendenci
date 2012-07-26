from haystack import indexes
from haystack import site

from tendenci.core.perms.indexes import TendenciBaseSearchIndex

from tendenci.apps.case_studies.models import CaseStudy, Image

class CaseStudyIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    client = indexes.CharField(model_attr='client')
    service = indexes.CharField(model_attr='services')
    technology = indexes.CharField(model_attr='technologies')

site.register(CaseStudy, CaseStudyIndex)
site.register(Image)
