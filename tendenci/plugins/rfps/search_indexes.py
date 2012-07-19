from haystack import indexes
from haystack import site

from perms.indexes import TendenciBaseSearchIndex
from rfps.models import RFP

class RFPIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name',)
    slug = indexes.CharField(model_attr='slug')
    program = indexes.CharField(model_attr='program')
    status = indexes.CharField(model_attr='status',)
    release_dt = indexes.DateTimeField(model_attr='release_dt',)
    proposal_due_dt = indexes.DateTimeField(model_attr='proposal_due_dt',)
    expired_dt = indexes.DateTimeField(model_attr='expired_dt',)
    questions_title = indexes.CharField(model_attr='questions_title',)
    questions_expiration_dt = indexes.DateTimeField(model_attr='questions_expiration_dt',)
    contract_doc_description = indexes.CharField(model_attr='contract_doc_description',)

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(RFP, RFPIndex)
