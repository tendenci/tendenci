from datetime import datetime
from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from directories.models import Directory
from perms.models import ObjectPermission
from categories.models import Category

class DirectoryIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    headline = indexes.CharField(model_attr='headline', faceted=True)
    body = indexes.CharField(model_attr='body')
    activation_dt = indexes.DateTimeField(model_attr='activation_dt', null=True)
    expiration_dt = indexes.DateTimeField(model_attr='expiration_dt', null=True)
    syndicate = indexes.BooleanField(model_attr='syndicate')
    
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
    
    who_can_view = indexes.CharField()

    category = indexes.CharField()
    sub_category = indexes.CharField()

    # for rss
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()
    
    #for primary key: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')
    
    def prepare_can_syndicate(self, obj):
        args = [
            obj.allow_anonymous_view,
            obj.syndicate,
            obj.status,
            obj.status_detail=='active',
        ]

        if obj.activation_dt:
            args.append(obj.activation_dt <= datetime.now())
            
        if obj.expiration_dt:
            args.append(obj.expiration_dt > datetime.now())

        return all(args)
        
    def prepare_order(self, obj):
        return obj.activation_dt
    
    def prepare_category(self, obj):
        category = Category.objects.get_for_object(obj, 'category')
        if category: return category.name
        return ''
    
    def prepare_sub_category(self, obj):
        category = Category.objects.get_for_object(obj, 'sub_category')
        if category: return category.name
        return ''      
    
    def prepare_who_can_view(self, obj):
        users = ObjectPermission.objects.who_has_perm('directories.view_directory', obj)
        user_list = []
        if users:
            for user in users:
                user_list.append(user.username)
            return ','.join(user_list)
        else: 
            return ''
    
    def prepare_body(self, obj):
        body = obj.body
        body = strip_tags(body)
        body = strip_entities(body)
        return body
    
site.register(Directory, DirectoryIndex)
