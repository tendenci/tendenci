from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from event_logs.managers import EventLogManager
from entities.models import Entity
from robots.models import Robot

class EventLog(models.Model):
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
 
    def get_absolute_url(self):
        return ('event_log', [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)
           
    def __unicode__(self):
        return str(self.event_id)

