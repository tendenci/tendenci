from haystack import indexes

from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

from tendenci.apps.case_studies.models import CaseStudy

class CaseStudyIndex(TendenciBaseSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    client = indexes.CharField(model_attr='client')
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return CaseStudy

    def prepare_order(self, obj):
        return obj.update_dt