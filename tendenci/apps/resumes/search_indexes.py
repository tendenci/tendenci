from haystack import indexes


from django.utils.html import strip_tags, strip_entities

from tendenci.apps.resumes.models import Resume
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class ResumeIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    activation_dt = indexes.DateTimeField(model_attr='activation_dt', null=True)
    expiration_dt = indexes.DateTimeField(model_attr='expiration_dt', null=True)
    syndicate = indexes.BooleanField(model_attr='syndicate', null=True)

    @classmethod
    def get_model(self):
        return Resume

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description


