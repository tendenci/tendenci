from django.utils.html import strip_tags, strip_entities

from haystack import indexes

from tendenci.apps.forms_builder.forms.models import Form
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex

class FormsIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    intro = indexes.CharField(model_attr='intro')
    response = indexes.CharField(model_attr='response')

    @classmethod
    def get_model(self):
        return Form

    def prepare_intro(self, obj):
        intro = obj.intro
        intro = strip_tags(intro)
        intro = strip_entities(intro)
        return intro

    def prepare_response(self, obj):
        response = obj.response
        response = strip_tags(response)
        response = strip_entities(response)
        return response


