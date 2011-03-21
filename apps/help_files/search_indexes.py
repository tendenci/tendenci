from datetime import datetime

from haystack import indexes
from haystack import site
from django.utils.html import strip_tags, strip_entities

from models import HelpFile
from perms.models import ObjectPermission

class HelpFileIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    question = indexes.CharField(model_attr='question')
    answer = indexes.CharField(model_attr='answer')
    syndicate = indexes.BooleanField(model_attr='syndicate')
    topic = indexes.CharField()
    
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
    
    # for rss
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()
    
    #for primary key: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')
    
    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.syndicate \
                and obj.status==1  and obj.status_detail=='active' \
                and obj.create_dt <= datetime.now()
        
    def prepare_order(self, obj):
        return obj.create_dt
    
    def prepare_who_can_view(self, obj):
        users = ObjectPermission.objects.who_has_perm('help_files.view_helpfile', obj)
        user_list = []
        if users:
            for user in users:
                user_list.append(user.username)
            return ','.join(user_list)
        else: 
            return ''
    
    def prepare_topic(self, obj):
        topics = obj.topics.all()
        if topics:
            return ','.join([t.title for t in topics])
        return ''
        
    def prepare_answer(self, obj):
        answer = obj.answer
        answer = strip_tags(answer)
        answer = strip_entities(answer)
        return answer

site.register(HelpFile, HelpFileIndex)
