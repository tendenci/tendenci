from haystack import indexes
from haystack import site
from models import HelpFile

class HelpIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)

site.register(HelpFile, HelpIndex)
