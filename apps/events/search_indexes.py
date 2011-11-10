from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from events.models import Event, Registrant
from events.utils import count_event_spots_taken
from events.models import Type as EventType
from perms.indexes import TendenciBaseSearchIndex
from perms.object_perms import ObjectPermission

class EventIndex(TendenciBaseSearchIndex):
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    start_dt = indexes.DateTimeField(model_attr='start_dt')
    end_dt = indexes.DateTimeField(model_attr='end_dt')
    on_weekend = indexes.BooleanField(model_attr='on_weekend')
    
    # event type id
    type_id = indexes.IntegerField(null=True)
    
    # amount of registrations spots left
    spots_taken = indexes.IntegerField()
    
    # number of days the event is active
    number_of_days = indexes.IntegerField()
    
    # RSS fields
    can_syndicate = indexes.BooleanField()
    
    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description
        
    def prepare_type_id(self, obj):
        if obj.type:
            return obj.type.pk
        else:
            return None

    def prepare_spots_taken(self, obj):
        if hasattr(obj, 'spots_taken'):
            return obj.spots_taken
        else:
            return count_event_spots_taken(obj)
            
    def prepare_number_of_days(self, obj):
        return obj.number_of_days()

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
                and obj.status_detail == 'active'


class EventTypeIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    slug = indexes.CharField(model_attr='slug')

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')


class RegistrantIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    event_pk = indexes.IntegerField(model_attr='registration__event__pk')
    cancel_dt = indexes.DateTimeField(model_attr='cancel_dt', null=True)
    create_dt = indexes.DateTimeField(model_attr='create_dt')
    update_dt = indexes.DateTimeField(model_attr='update_dt')
    last_name = indexes.CharField(model_attr='last_name')

    # permission fields
    users_can_view = indexes.MultiValueField()
    groups_can_view = indexes.MultiValueField()

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'

    def prepare_users_can_view(self, obj):
        user_ids = ObjectPermission.objects.users_with_perms('registrants.view_registrant', obj)

        if obj.user:  # include the user bound to the registrant record
            user_ids.append(obj.user.pk)

        return user_ids

    def prepare_groups_can_view(self, obj):
        return ObjectPermission.objects.groups_with_perms('registrants.view_registrant', obj)

site.register(Event, EventIndex)
site.register(EventType, EventTypeIndex)
site.register(Registrant, RegistrantIndex)
