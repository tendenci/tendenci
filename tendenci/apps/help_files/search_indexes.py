from datetime import datetime
from haystack import indexes

from tendenci.apps.help_files.models import HelpFile
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.base.utils import strip_html


class HelpFileIndex(TendenciBaseSearchIndex, indexes.Indexable):
    question = indexes.CharField(model_attr='question')
    answer = indexes.CharField(model_attr='answer')
    syndicate = indexes.BooleanField(model_attr='syndicate', null=True)
    topic = indexes.MultiValueField()

    # RSS field
    can_syndicate = indexes.BooleanField(null=True)
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return HelpFile

    def prepare_answer(self, obj):
        return strip_html(obj.answer)

    def prepare_topic(self, obj):
        return [topic.pk for topic in obj.topics.all()]

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.syndicate \
                and obj.status == 1 and obj.status_detail == 'active' \
                and obj.create_dt <= datetime.now()

    def prepare_order(self, obj):
        return obj.create_dt
