from datetime import datetime
from haystack import indexes


from django.utils.html import strip_tags, strip_entities

from tendenci.apps.help_files.models import HelpFile
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

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
        answer = obj.answer
        answer = strip_tags(answer)
        answer = strip_entities(answer)
        return answer

    def prepare_topic(self, obj):
        return [topic.pk for topic in obj.topics.all()]

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.syndicate \
                and obj.status == 1  and obj.status_detail == 'active' \
                and obj.create_dt <= datetime.now()

    def prepare_order(self, obj):
        return obj.create_dt


