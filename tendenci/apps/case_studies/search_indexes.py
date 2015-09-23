from haystack import indexes

from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

from tendenci.apps.case_studies.models import CaseStudy, Image

class CaseStudyIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    client = indexes.CharField(model_attr='client')

    @classmethod
    def get_model(self):
        return CaseStudy
