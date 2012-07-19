from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex
from trainings.models import Training, Completion

class TrainingIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    training_type = indexes.CharField(model_attr='training_type')
    points = indexes.DecimalField(model_attr='points')

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt


class CompletionIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    finish_dt = indexes.DateTimeField(model_attr='finish_dt')

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(Training, TrainingIndex)
site.register(Completion, CompletionIndex)
