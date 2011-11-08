from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex
from plugs.models import Plug

class PlugIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    number = indexes.IntegerField(model_attr='number')
    brother = indexes.CharField(model_attr='brother')
    multiline_one = indexes.CharField(model_attr='multiline_one')
    start = indexes.DateTimeField(model_attr='start')

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(Plug, PlugIndex)
