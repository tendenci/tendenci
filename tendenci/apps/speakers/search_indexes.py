from haystack import indexes


from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

from tendenci.apps.speakers.models import Speaker

class SpeakerIndex(TendenciBaseSearchIndex):
    name = indexes.CharField(model_attr='name')
    company = indexes.CharField(model_attr='company', null=True)
    position = indexes.CharField(model_attr='position', null=True)
    track = indexes.CharField(model_attr='track', null=True)
    ordering = indexes.IntegerField(model_attr='ordering', null=True)

    @classmethod
    def get_model(self):
        return Speaker
