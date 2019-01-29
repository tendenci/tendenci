from builtins import str
from haystack import indexes

from tendenci.apps.events.models import Event, Registrant
from tendenci.apps.events.utils import count_event_spots_taken
from tendenci.apps.perms.indexes import TendenciBaseSearchIndex
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.search.indexes import CustomSearchIndex
from tendenci.apps.base.utils import strip_html


class EventIndex(TendenciBaseSearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    start_dt = indexes.DateTimeField(model_attr='start_dt')
    end_dt = indexes.DateTimeField(model_attr='end_dt')
    on_weekend = indexes.BooleanField(model_attr='on_weekend', null=True)

    # fields for sorting events that span multiple days
    hour = indexes.IntegerField()
    minute = indexes.IntegerField()

    # event type id
    type_id = indexes.IntegerField(null=True)

    # amount of registrations spots left
    spots_taken = indexes.IntegerField()

    # number of days the event is active
    number_of_days = indexes.IntegerField()

    # RSS fields
    can_syndicate = indexes.BooleanField(null=True)
    order = indexes.DateTimeField()

    @classmethod
    def get_model(self):
        return Event

    def prepare_description(self, obj):
        return strip_html(obj.description)

    def prepare_hour(self, obj):
        return int(obj.start_dt.hour)

    def prepare_minute(self, obj):
        return int(obj.start_dt.minute)

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

    def prepare_order(self, obj):
        return obj.start_dt
