import uuid
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from timezones.fields import TimeZoneField
from entities.models import Entity
from events.managers import EventManager
from perms.models import TendenciBaseModel 
from django import forms

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

class Phone(): pass
class Email(): pass

class Registrant(models.Model):
    """
    Event registrant.
    An event can have multiple registrants.
    A registrant can go to multiple events.
    A registrant is static information.
    The names do not change nor does their information
    This is the information that was used while registering
    """
    event = models.ManyToManyField('Event', editable=False)

    name = models.CharField(max_length=100)
    mail_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    groups = models.CharField(max_length=100)     

    company_name = models.CharField(max_length=100)
    
    

#class Registration(models.Model):
#    """
#    Registration record.
#    Created every time a user successfully registers.
#    Holds valuable information about their registration.
#    Used mostly for proof-of-registration.
#    Also used for metrics; how many people registered for event.
#    """
#
#    event = models.OneToOneField('Event', editable=False)
#    price = models.DecimalField(max_digits=21, decimal_places=2)
#    limit = models.IntegerField()

class Registration(models.Model):
    guid = models.TextField(max_length=40, editable=False, default=uuid.uuid1)

    event = models.ForeignKey('Event') # dynamic (should be static)

    invoiceid = models.IntegerField(null=True, blank=True) # proof of transaction
    subsidy = models.BooleanField(null=True, blank=True)

    discountcode = models.CharField(max_length=50)
    discountamount = models.DecimalField(null=True, max_digits=21, decimal_places=4, blank=True)

    paid = models.IntegerField()
    paidcheck = models.IntegerField()
    secured = models.IntegerField()
    offline = models.IntegerField()

#    creator = models.ForeignKey('User')
#    owner = models.ForeignKey('User')
#    create_dt = models.DateField()
#    update_dt = models.DateField()
#    status = models.IntegerField()

    submitdate = models.DateTimeField()

    owneruserid = models.IntegerField()
    ownerusername = models.TextField()

    exported = models.BooleanField(null=True, blank=True)

    registrationtable = models.TextField(blank=True)
    registrationnotes = models.TextField(blank=True)
    registrationteam = models.TextField(blank=True)

    reminder = models.BooleanField(null=True, blank=True)

    pricechoice = models.CharField(max_length=75, blank=True)


# TODO: use shorter name
class RegistrationConfiguration(models.Model):
    """
    Event registration
    Extends the event model
    """
    event = models.OneToOneField('Event', editable=False)
    # TODO: do not use fixtures, use RAWSQL to prepopulate
    # TODO: set widget here instead of within form class
    payment_methods = models.ManyToManyField('PaymentMethod')
    
    early_price = models.DecimalField(_('Early Price'), max_digits=21, decimal_places=2)
    regular_price = models.DecimalField(_('Regular Price'), max_digits=21, decimal_places=2)
    late_price = models.DecimalField(_('Late Price'), max_digits=21, decimal_places=2)

    early_dt = models.DateTimeField(_('Early Date'))
    regular_dt = models.DateTimeField(_('Regular Date'))
    late_dt = models.DateTimeField(_('Late Date'))
    
    limit = models.IntegerField()

    enabled = models.BooleanField()

class Payment(models.Model):
    """
    Event registration payment
    Extends the registration model
    """
#    METHODS = ('Credit Card', 'Check', 'Cash', 'At Event')
    registration = models.OneToOneField('Registration')
#    methods_available = models.CharField(max_length=50, choices=METHODS, default='active')

class PaymentMethod(models.Model):
    """
    This will hold available payment methods
    Default payment methods are 'Credit Card, Cash and Check.'
    Pre-populated via fixtures
    """
    label = models.CharField(max_length=50)

    def __unicode__(self):
        return self.label

#class PaymentPeriod(models.Model):
#    """
#    Defines the time-range and price a registrant must pay.
#    e.g. (early price, regular price, late price) 
#    """
#    label = models.CharField(max_length=50)
#    start_dt = models.DateTimeField()
#    end_dt = models.DateTimeField()
#    price = models.DecimalField(max_digits=21, decimal_places=2)
#    registration_confirmation = models.ForeignKey('RegistrationConfiguration', related_name='payment_period')

    # TODO: price per group
    # anonymous (is not a group or is a dynamic group)
    # registered (is not a group or is a dynamic group)
#    anon_price = models.DecimalField(max_digits=21, decimal_places=2)
#    auth_price = models.DecimalField(max_digits=21, decimal_places=2)
#    group_price = models.ForeignKey('GroupPrice') # not the same as group-pricing

#    def __unicode__(self):
#        return self.label


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
    guid = models.TextField(max_length=40, editable=False, default=uuid.uuid1)
    entity = models.ForeignKey(Entity, null=True)

    type = models.ForeignKey(Type, blank=True, null=True)

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

    def __unicode__(self):
        return self.title


