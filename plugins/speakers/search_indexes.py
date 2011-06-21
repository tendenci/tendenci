from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex

from models import Speaker

class SpeakerIndex(TendenciBaseSearchIndex):
    name = indexes.CharField(model_attr='name')
    company = indexes.CharField(model_attr='company', null=True)
    position = indexes.CharField(model_attr='position', null=True)
    track = indexes.CharField(model_attr='track', null=True)

site.register(Speaker, SpeakerIndex)
