from haystack import indexes

from tendenci.apps.pages.models import Page
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.categories.models import Category
from tendenci.apps.base.utils import strip_html


class PageIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    content = indexes.CharField(model_attr='content')
    syndicate = indexes.BooleanField(model_attr='syndicate', null=True)

    # categories
    category = indexes.CharField()
    sub_category = indexes.CharField()

    # RSS fields
    can_syndicate = indexes.BooleanField(null=True)
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return Page

    def prepare_content(self, obj):
        return strip_html(obj.content)

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
        return obj.allow_anonymous_view and obj.syndicate and obj.status == 1  \
            and obj.status_detail == 'active'

    def prepare_order(self, obj):
        return obj.update_dt
