from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from pages.models import Page
from perms.models import ObjectPermission

class PageIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    content = indexes.CharField(model_attr='content')
    create_dt = indexes.DateTimeField(model_attr='create_dt', null=True)

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
    
    def prepare_who_can_view(self, obj):
        users = ObjectPermission.objects.who_has_perm('pages.view_page', obj)
        user_list = []
        if users:
            for user in users:
                user_list.append(user.username)
            return ','.join(user_list)
        else: 
            return ''
               
    def prepare_content(self, obj):
        content = obj.content
        content = strip_tags(content)
        content = strip_entities(content)
        return content
    
site.register(Page, PageIndex)