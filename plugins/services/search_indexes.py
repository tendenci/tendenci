from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from models import Service
from perms.models import ObjectPermission

class ServiceIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description') 

    activation_dt = indexes.DateTimeField(model_attr='activation_dt', null=True)
    expiration_dt = indexes.DateTimeField(model_attr='expiration_dt', null=True)
    
    create_dt = indexes.DateTimeField(model_attr='create_dt')
    syndicate = indexes.BooleanField(model_attr='syndicate')

    # authority fields
    allow_anonymous_view = indexes.BooleanField(model_attr='allow_anonymous_view')
    allow_user_view = indexes.BooleanField(model_attr='allow_user_view')
    allow_member_view = indexes.BooleanField(model_attr='allow_member_view')
    allow_anonymous_edit = indexes.BooleanField(model_attr='allow_anonymous_edit')
    allow_user_edit = indexes.BooleanField(model_attr='allow_user_edit')
    allow_member_edit = indexes.BooleanField(model_attr='allow_member_edit')
    creator = indexes.CharField(model_attr='creator', null=True)
    creator_username = indexes.CharField(model_attr='creator_username', null=True)
    owner = indexes.CharField(model_attr='owner', null=True)
    owner_username = indexes.CharField(model_attr='owner_username', null=True)
    status = indexes.IntegerField(model_attr='status')
    status_detail = indexes.CharField(model_attr='status_detail')
    
    who_can_view = indexes.CharField()
    
    #for primary key: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'

    def prepare_who_can_view(self, obj):
        users = ObjectPermission.objects.who_has_perm('services.view_service', obj)
        user_list = []
        if users:
            for user in users:
                user_list.append(user.username)
            return ','.join(user_list)
        else: 
            return ''
    
    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description
    
site.register(Service, ServiceIndex)
