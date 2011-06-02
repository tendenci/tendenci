import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from event_logs.managers import EventLogManager
from entities.models import Entity
from robots.models import Robot
from event_logs.colors import get_color

class EventLog(models.Model):
    guid = models.CharField(max_length=40) 
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.IntegerField(null=True)
    source = models.CharField(max_length=50, null=True)
    entity = models.ForeignKey(Entity, null=True)
    event_id = models.IntegerField()
    event_name = models.CharField(max_length=50)
    event_type = models.CharField(max_length=50)
    event_data = models.TextField()
    category = models.CharField(max_length=50, null=True)
    session_id = models.CharField(max_length=40, null=True)
    user = models.ForeignKey(User, null=True)
    username = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)
    user_ip_address = models.IPAddressField(null=True)
    server_ip_address = models.IPAddressField(null=True)
    url = models.URLField(max_length=255, null=True)
    http_referrer = models.URLField(max_length=255, null=True)
    headline = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=120, null=True)
    http_user_agent = models.TextField(null=True)
    request_method = models.CharField(max_length=10, null=True)
    query_string = models.TextField(null=True)
    robot = models.ForeignKey(Robot, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    
    objects = EventLogManager()

    class Meta:
        permissions = (("view_eventlog","Can view eventlog"),)

    def color(self):
        return get_color(str(self.event_id))

    def get_absolute_url(self):
        return ('event_log', [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)

    def save(self):
        if not self.id:
            self.guid = uuid.uuid1()

        super(EventLog, self).save()

    def __unicode__(self):
        return str(self.event_id)


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
                cls._cache[key] = cls.objects.get(**{field:key}).hex_color
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
        return cls.cache_get(source, 'source') or '333333' # indeed some 
    
class EventLogColor(CachedColorModel):
    """
        Event Log Colors is for reporting only
    """
    event_id = models.IntegerField()
    hex_color = models.CharField(max_length=6)
    rgb_color = models.CommaSeparatedIntegerField(max_length=11)
    
    @classmethod
    def get_color(cls, event_id):
        return cls.cache_get(event_id, 'event_id') or '333333'
