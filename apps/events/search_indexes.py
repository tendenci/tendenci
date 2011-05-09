from django.utils.html import strip_tags, strip_entities

from haystack import indexes
from haystack import site
from events.models import Event, Registrant
from perms.object_perms import ObjectPermission
from events.models import Type as EventType


class EventIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    start_dt = indexes.DateTimeField(model_attr='start_dt')

    # TendenciBaseModel Fields
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

    # permission fields
    users_can_view = indexes.MultiValueField()
    groups_can_view = indexes.MultiValueField()

    # RSS fields
    can_syndicate = indexes.BooleanField()

    # PK: needed for exclude list_tags
    primary_key = indexes.CharField(model_attr='pk')

    def get_updated_field(self):
        return 'update_dt'

    def prepare_description(self, obj):
        description = obj.description
        description = strip_tags(description)
        description = strip_entities(description)
        return description

    def prepare_users_can_view(self, obj):
        return ObjectPermission.objects.users_with_perms('events.view_event', obj)

    def prepare_groups_can_view(self, obj):
        return ObjectPermission.objects.groups_with_perms('events.view_event', obj)

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
        return ObjectPermission.objects.users_with_perms('registrants.view_registrant', obj)

    def prepare_groups_can_view(self, obj):
        return ObjectPermission.objects.groups_with_perms('registrants.view_registrant', obj)

site.register(Event, EventIndex)
site.register(EventType, EventTypeIndex)
site.register(Registrant, RegistrantIndex)
