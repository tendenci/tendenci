import uuid
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from timezones.fields import TimeZoneField
from entities.models import Entity
from events.managers import EventManager
from perms.models import TendenciBaseModel 

class Type(models.Model):
    """
    Event Type
    Types is a way of grouping events
    An event can only be one type
    A type can have multiple events
    """
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Place(models.Model):
    """
    Event Place (location)
    An event can only be in one place
    A place can be used for multiple events
    """
    event = models.ForeignKey('Event', editable=False)

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    # geo location
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    zip = models.CharField(max_length=150)
    country = models.CharField(max_length=150)

    # online location
    url = models.URLField()
    

class Registrant(models.Model):
    """
    Event registrant
    An event can have multiple registrants
    A registrant can go to multiple events
    """
    event = models.ManyToManyField('Event', editable=False)

class Registration(models.Model):
    """
    Event registration
    Extends the event model
    """
    event = models.OneToOneField('Event', editable=False)
    price = models.DecimalField(max_digits=21, decimal_places=2)
    limit = models.IntegerField()

class Payment(models.Model):
    """
    Event registration payment
    Extends the registration model
    """
#    METHODS = ('Credit Card', 'Check', 'Cash', 'At Event')
    registration = models.OneToOneField('Registration')
#    methods_available = models.CharField(max_length=50, choices=METHODS, default='active')

class Sponsor(models.Model):
    """
    Event sponsor
    Event can have multiple sponsors
    Sponsor can contribute to multiple events
    """
    event = models.ManyToManyField('Event')

class Discount(models.Model):
    """
    Event discount
    Event can have multiple discounts
    Discount can only be associated with one event
    """
    event = models.ForeignKey('Event')
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)

class Organizer(models.Model):
    """
    Event organizer
    Event can have multiple organizers
    Organizer can maintain multiple events
    """
    event = models.ManyToManyField('Event')
    user = models.OneToOneField(User)

class Speaker(models.Model):
    """
    Event speaker
    Event can have multiple speakers
    Speaker can attend multiple events
    """
    event = models.ManyToManyField('Event')
    user = models.OneToOneField(User)

class Event(models.Model):
    """
    Calendar Event
    """
    guid = models.TextField(max_length=40, editable=False)
    entity = models.ForeignKey(Entity, null=True)

    type = models.ForeignKey(Type, blank=True)

    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    start_dt = models.DateTimeField(default=datetime.now())
    end_dt = models.DateTimeField(default=datetime.now())
    timezone = TimeZoneField(_('Time Zone'))

    private = models.BooleanField() # hide from lists
    password = models.CharField(max_length=50, blank=True)

    objects = EventManager()

    @models.permalink
    def get_absolute_url(self):
        return ("event", [self.pk])
    
    def save(self):
        if not self.id:
            self.guid = uuid.uuid1()
            
        super(self.__class__, self).save()
