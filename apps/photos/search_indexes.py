from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from photos.models import PhotoSet

class PhotoSetIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')
    update_dt = indexes.DateTimeField(model_attr='update_dt', null=True)
    
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
    
    # for rss
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()
    
    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status==1  and obj.status_detail=='active'
        
    def prepare_syndicate_order(self, obj):
        return obj.update_dt
    
    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description
    
site.register(PhotoSet, PhotoSetIndex)