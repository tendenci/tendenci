from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from tendenci.apps.events.models import Event, Type, Place


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'name']


class EventPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'virtual', 'description',
                  'address', 'city', 'state', 'zip',
                  'country', 'national', 'url']


class EventSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField()
    type = EventTypeSerializer(read_only=True)
    place = EventPlaceSerializer(read_only=True)
    class Meta:
        model = Event
        fields = ["id", "title", "type", "event_code", "description",
                  'start_dt', 'end_dt', 'groups', 'timezone', 'place',
                  "status_detail"]