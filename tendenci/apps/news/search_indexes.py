from datetime import datetime
from haystack import indexes


from django.utils.html import strip_tags, strip_entities

from tendenci.apps.news.models import News
from tendenci.apps.categories.models import Category
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex


class NewsIndex(TendenciBaseSearchIndex, indexes.Indexable):
    headline = indexes.CharField(model_attr='headline')
    source = indexes.CharField(model_attr='source')
    body = indexes.CharField(model_attr='body')
    release_dt = indexes.DateTimeField(model_attr='release_dt', null=True)
    release_dt_local = indexes.DateTimeField(model_attr='release_dt_local', null=True)
    syndicate = indexes.BooleanField(model_attr='syndicate', null=True)
    tags = indexes.CharField(model_attr='tags')

    # categories
    category = indexes.CharField()
    sub_category = indexes.CharField()

    # RSS fields
    can_syndicate = indexes.BooleanField(null=True)
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return News

    def prepare_body(self, obj):
        body = obj.body
        body = strip_tags(body)
        body = strip_entities(body)
        return body

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
                and obj.status == 1  and obj.status_detail == 'active' \
                and obj.release_dt <= datetime.now()

    def prepare_order(self, obj):
        return obj.release_dt


