from haystack import indexes
from haystack import site

from django.utils.html import strip_tags, strip_entities

from tendenci.apps.boxes.models import Box
from tendenci.core.perms.indexes import TendenciBaseSearchIndex


class BoxIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    content = indexes.CharField(model_attr='content')

    # RSS fields
    order = indexes.DateTimeField()

    def prepare_content(self, obj):
        content = obj.content
        content = strip_tags(content)
        content = strip_entities(content)
        return content

    def prepare_order(self, obj):
        return obj.update_dt

site.register(Box, BoxIndex)
