from haystack import indexes

from tendenci.apps.jobs.models import Job
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.base.utils import strip_html


class JobIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    list_type = indexes.CharField(model_attr='list_type')
    description = indexes.CharField(model_attr='description')
    post_dt = indexes.DateTimeField(model_attr='post_dt', null=True)
    syndicate = indexes.BooleanField(model_attr='syndicate', null=True)

    # categories
    cat = indexes.CharField()
    sub_cat = indexes.CharField()

    # RSS fields
    can_syndicate = indexes.BooleanField(null=True)

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    #overriden fields
    creator = indexes.CharField(model_attr='creator', null=True)
    creator_username = indexes.CharField(model_attr='creator_username', null=True)
    owner = indexes.CharField(model_attr='owner', null=True)
    owner_username = indexes.CharField(model_attr='owner_username', null=True)

    @classmethod
    def get_model(self):
        return Job

    def prepare_description(self, obj):
        return strip_html(obj.description)

    def prepare_cate(self, obj):
        category = obj.cat
        if category:
            return category.name
        return ''

    def prepare_sub_cat(self, obj):
        category = obj.sub_cat
        if category:
            return category.name
        return ''

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.syndicate \
                and obj.status == 1 and obj.status_detail == 'active'
