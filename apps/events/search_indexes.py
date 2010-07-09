from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from events.models import Event
from perms.models import ObjectPermission

class EventIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
#    create_dt = indexes.DateTimeField(model_attr='create_dt')
    
    who_can_view = indexes.CharField()

    def prepare_who_can_view(self, obj):
        users = ObjectPermission.objects.who_has_perm('events.view_event', obj)
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
    
site.register(Event, EventIndex)