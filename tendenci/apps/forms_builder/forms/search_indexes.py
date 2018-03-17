from haystack import indexes

from tendenci.apps.forms_builder.forms.models import Form
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.base.utils import strip_html


class FormsIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    intro = indexes.CharField(model_attr='intro')
    response = indexes.CharField(model_attr='response')

    @classmethod
    def get_model(self):
        return Form

    def prepare_intro(self, obj):
        return strip_html(obj.intro)

    def prepare_response(self, obj):
        return strip_html(obj.response)
