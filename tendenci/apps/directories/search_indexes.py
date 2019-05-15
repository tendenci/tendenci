from datetime import datetime
from haystack import indexes

from tendenci.apps.directories.models import Directory
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.categories.models import Category
from tendenci.apps.base.utils import strip_html


class DirectoryIndex(TendenciBaseSearchIndex, indexes.Indexable):
    headline = indexes.CharField(model_attr='headline', faceted=True)
    body = indexes.CharField(model_attr='body')
    activation_dt = indexes.DateTimeField(model_attr='activation_dt', null=True)
    expiration_dt = indexes.DateTimeField(model_attr='expiration_dt', null=True)
    syndicate = indexes.BooleanField(model_attr='syndicate', null=True)

    # categories
    category = indexes.CharField()
    sub_category = indexes.CharField()

    # RSS fields
    can_syndicate = indexes.BooleanField(null=True)
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return Directory

    def prepare_body(self, obj):
        return strip_html(obj.body)

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
        args = [
            obj.allow_anonymous_view,
            obj.syndicate,
            obj.status,
            obj.status_detail == 'active',
        ]

        if obj.activation_dt:
            args.append(obj.activation_dt <= datetime.now())

        if obj.expiration_dt:
            args.append(obj.expiration_dt > datetime.now())

        return all(args)

    def prepare_order(self, obj):
        if obj.activation_dt:
            return obj.activation_dt
        return obj.create_dt
