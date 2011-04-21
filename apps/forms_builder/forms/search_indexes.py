from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from forms_builder.forms.models import Form

class FormsIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    
    title = indexes.CharField(model_attr='title')
    intro = indexes.CharField(model_attr='intro')
    response = indexes.CharField(model_attr='response')

    # authority fields
    allow_anonymous_view = indexes.BooleanField(model_attr='allow_anonymous_view')
    allow_user_view = indexes.BooleanField(model_attr='allow_user_view')
    allow_member_view = indexes.BooleanField(model_attr='allow_member_view')
    allow_anonymous_edit = indexes.BooleanField(model_attr='allow_anonymous_edit')
    allow_user_edit = indexes.BooleanField(model_attr='allow_user_edit')
    allow_member_edit = indexes.BooleanField(model_attr='allow_member_edit')
    creator = indexes.CharField(model_attr='creator')
    creator_username = indexes.CharField(model_attr='creator_username')
    owner = indexes.CharField(model_attr='owner')
    owner_username = indexes.CharField(model_attr='owner_username')
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')
    
    #for primary key: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'

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
        
site.register(Form, FormsIndex)
