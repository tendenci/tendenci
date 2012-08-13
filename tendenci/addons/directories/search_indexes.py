from datetime import datetime
from haystack import indexes
from haystack import site

from django.utils.html import strip_tags, strip_entities

from tendenci.addons.directories.models import Directory
from tendenci.core.perms.indexes import TendenciBaseSearchIndex
from tendenci.core.categories.models import Category

class DirectoryIndex(TendenciBaseSearchIndex):
    headline = indexes.CharField(model_attr='headline', faceted=True)
    body = indexes.CharField(model_attr='body')
    activation_dt = indexes.DateTimeField(model_attr='activation_dt', null=True)
    expiration_dt = indexes.DateTimeField(model_attr='expiration_dt', null=True)
    syndicate = indexes.BooleanField(model_attr='syndicate')

    # categories
    category = indexes.CharField()
    sub_category = indexes.CharField()

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

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
        return obj.activation_dt

site.register(Directory, DirectoryIndex)
