from haystack import indexes
from haystack import site

from django.utils.html import strip_tags, strip_entities

from tendenci.addons.jobs.models import Job
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.categories.models import Category
from tendenci.core.perms.indexes import TendenciBaseSearchIndex

class JobIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    list_type = indexes.CharField(model_attr='list_type')
    description = indexes.CharField(model_attr='description')
    post_dt = indexes.DateTimeField(model_attr='post_dt', null=True)
    syndicate = indexes.BooleanField(model_attr='syndicate')

    # categories
    category = indexes.CharField()
    sub_category = indexes.CharField()

    # RSS fields
    can_syndicate = indexes.BooleanField()

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    #overriden fields
    creator = indexes.CharField(model_attr='creator', null=True)
    creator_username = indexes.CharField(model_attr='creator_username', null=True)
    owner = indexes.CharField(model_attr='owner', null=True)
    owner_username = indexes.CharField(model_attr='owner_username', null=True)

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description

    def prepare_category(self, obj):
        category = Category.objects.get_for_object(obj, 'category')
        if category:
            return category.name
        return ''

    def prepare_sub_category(self, obj):
        category = Category.objects.get_for_object(obj, 'sub_category')
        if category:
            return category.name
        return ''

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.syndicate \
                and obj.status == 1 and obj.status_detail == 'active'

site.register(Job, JobIndex)
