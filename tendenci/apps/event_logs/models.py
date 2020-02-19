import uuid
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import validate_comma_separated_integer_list

from tendenci.apps.event_logs.managers import EventLogManager
from tendenci.apps.entities.models import Entity
from tendenci.apps.robots.models import Robot
from tendenci.apps.event_logs.colors import get_color


class EventLog(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    object_id = models.IntegerField(null=True)
    source = models.CharField(max_length=50, null=True)
    entity = models.ForeignKey(Entity, null=True, on_delete=models.SET_NULL)
    event_id = models.IntegerField()
    event_name = models.CharField(max_length=50)
    event_type = models.CharField(max_length=50)
    event_data = models.TextField()
    category = models.CharField(max_length=50, null=True)
    session_id = models.CharField(max_length=40, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    username = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)
    user_ip_address = models.GenericIPAddressField(null=True)
    server_ip_address = models.GenericIPAddressField(null=True)
    url = models.URLField(max_length=255, null=True)
    http_referrer = models.URLField(max_length=255, null=True)
    headline = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=120, null=True)
    http_user_agent = models.TextField(null=True)
    request_method = models.CharField(max_length=10, null=True)
    query_string = models.TextField(null=True)
    robot = models.ForeignKey(Robot, null=True, on_delete=models.SET_NULL)
    create_dt = models.DateTimeField(auto_now_add=True, db_index=True)

    uuid = models.CharField(max_length=40)
    application = models.CharField(max_length=50, db_index=True)
    action = models.CharField(max_length=50, db_index=True)
    model_name = models.CharField(max_length=75)

    objects = EventLogManager()

    class Meta:
#         permissions = (("view_eventlog", _("Can view eventlog")),)
        app_label="event_logs"

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        self.verifydata()
        super(EventLog, self).save(*args, **kwargs)
        
    def verifydata(self):
        # verify each field
        for field in EventLog._meta.fields:
            value = getattr(self, field.name)
            if field.max_length and value and len(value) > field.max_length:
                value = value[:field.max_length]
                setattr(self, field.name, value)

    def color(self):
        return get_color(str(self.event_id))

    def get_absolute_url(self):
        return reverse('event_log', args=[self.pk])

    def __str__(self):
        return str(self.event_id)

    def delete(self, *args, **kwargs):
        """
        Event logs are never deleted.
        Per Ed Schipul 9/19/2012
        """
        pass


class CachedColorModel(models.Model):
    "Cache to avoid re-looking up eventlog color objects all over the place."
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__._cache = {}
        super(CachedColorModel, self).save(*args, **kwargs)

    @classmethod
    def cache_get(cls, key, field):
        if not hasattr(cls, '_cache'):
            cls._cache = {}
        try:
            return cls._cache[key]
        except KeyError:
            try:
                cls._cache[key] = cls.objects.get(**{field: key}).hex_color
            except cls.DoesNotExist:
                return None
            return cls._cache[key]


class EventLogBaseColor(CachedColorModel):
    """
        Event Log Base Colors is for reporting only
    """
    source = models.CharField(max_length=50)
    event_id = models.IntegerField()
    hex_color = models.CharField(max_length=6)

    @classmethod
    def get_color(cls, source):
        return cls.cache_get(source, 'source') or '17ABB9'  # indeed some

    class Meta:
        app_label="event_logs"


class EventLogColor(CachedColorModel):
    """
        Event Log Colors is for reporting only
    """
    event_id = models.IntegerField()
    hex_color = models.CharField(max_length=6)
    rgb_color = models.CharField(max_length=11, validators=[validate_comma_separated_integer_list])

    @classmethod
    def get_color(cls, event_id):
        return cls.cache_get(event_id, 'event_id') or '333333'

    class Meta:
        app_label="event_logs"
