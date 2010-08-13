import uuid
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from timezones.fields import TimeZoneField
from entities.models import Entity
from events.managers import EventManager, RegistrantManager
from perms.models import TendenciBaseModel
from meta.models import Meta as MetaTags


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
    name = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    # offline location
    address = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=150, blank=True)
    zip = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=150, blank=True)

    # online location
    url = models.URLField(blank=True)

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
    registration = models.ForeignKey('Registration', null=True)
    user = models.ForeignKey(User)

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
    
    objects = RegistrantManager()

class Registration(models.Model):

    guid = models.TextField(max_length=40, editable=False, default=uuid.uuid1)
    event = models.ForeignKey('Event') # dynamic (should be static)

#    invoiceid = models.IntegerField(null=True, blank=True) # proof of transaction
#    discounts = models.ForeignKey('DiscountRedeemed')

    reminder = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    # payment methods are soft-deleted
    # this means they can always be referenced
    payment_method = models.ForeignKey('PaymentMethod')
    amount_paid = models.DecimalField(_('Amount Paid'), max_digits=21, decimal_places=2)

    creator = models.ForeignKey(User, related_name='created_registrations')
    owner = models.ForeignKey(User, related_name='owned_registrations')
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
#    status = models.BooleanField()

    def save_invoice(self, *args, **kwargs):
        from invoices.models import Invoice
        status_detail = kwargs.get('status_detail', 'estimate')

        try: # get invoice
            invoice = Invoice.objects.get(
                invoice_object_type = 'event_registration',
                invoice_object_type_id = self.pk,
            )
        except: # else; create invoice
            invoice = Invoice()
            invoice.invoice_object_type = 'event_registration'
            invoice.invoice_object_type_id = self.pk

        # update invoice with details
        invoice.estimate = True
        invoice.status_detail = status_detail
        invoice.subtotal = self.amount_paid
        invoice.total = self.amount_paid
        invoice.balance = self.amount_paid
        invoice.due_date = datetime.now()
        invoice.ship_date = datetime.now()
        invoice.save(self.creator) # TODO: update to user once field exists 

        return invoice
            

# TODO: use shorter name
class RegistrationConfiguration(models.Model):
    """
    Event registration
    Extends the event model
    """
    # TODO: do not use fixtures, use RAWSQL to prepopulate
    # TODO: set widget here instead of within form class
    payment_method = models.ManyToManyField('PaymentMethod')
    
    early_price = models.DecimalField(_('Early Price'), max_digits=21, decimal_places=2, default=0)
    regular_price = models.DecimalField(_('Regular Price'), max_digits=21, decimal_places=2, default=0)
    late_price = models.DecimalField(_('Late Price'), max_digits=21, decimal_places=2, default=0)

    early_dt = models.DateTimeField(_('Early Date'))
    regular_dt = models.DateTimeField(_('Regular Date'))
    late_dt = models.DateTimeField(_('Late Date'))

    limit = models.IntegerField(default=0)
    enabled = models.BooleanField(default=False)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        if hasattr(self,'event'):
        # registration_configuration might not be attached to an event yet

            # assume practical dates
            self.early_dt = self.create_dt
            self.regular_dt = self.create_dt 
            self.late_dt = self.event.start_dt
            
            self.PERIODS = {
                'early': (self.early_dt, self.regular_dt),
                'regular': (self.regular_dt, self.late_dt),
                'late': (self.late_dt, self.event.start_dt),
            }

        else:
            self.PERIODS = None

    def price(self):

        price = 0.00
        for period in self.PERIODS:
            if self.PERIODS[period][0] <= datetime.now() <= self.PERIODS[period][1]:
                price = self.price_from_period(period)

        return price

    def price_from_period(self, period):

        if period in self.PERIODS:
            return getattr(self, '%s_price' % period)
        else: return None
    


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
    Soft Deletes required; For historical purposes.
    """
    label = models.CharField(max_length=50, blank=False)

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
    event = models.ManyToManyField('Event', blank=True)
    user = models.OneToOneField(User, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True) # static info.
    description = models.TextField(blank=True) # static info.    

class Speaker(models.Model):
    """
    Event speaker
    Event can have multiple speakers
    Speaker can attend multiple events
    """
    event = models.ManyToManyField('Event', blank=True)
    user = models.OneToOneField(User, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True) # static info.
    description = models.TextField(blank=True) # static info.

class Event(TendenciBaseModel):
    """
    Calendar Event
    """
    guid = models.CharField(max_length=40, editable=False, default=uuid.uuid1)
    entity = models.ForeignKey(Entity, blank=True, null=True)

    type = models.ForeignKey(Type, blank=True, null=True)

    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    start_dt = models.DateTimeField(default=datetime.now())
    end_dt = models.DateTimeField(default=datetime.now())
    timezone = TimeZoneField(_('Time Zone'))

    place = models.ForeignKey('Place', null=True)
    registration_configuration = models.OneToOneField('RegistrationConfiguration', null=True, editable=False)

    private = models.BooleanField() # hide from lists
    password = models.CharField(max_length=50, blank=True)

    # html-meta tags
    meta = models.OneToOneField(MetaTags, null=True)

    objects = EventManager()

    @property
    def reg_conf(self):
        return self.registration_configuration

    @models.permalink
    def get_absolute_url(self):
        return ("event", [self.pk])

    def __unicode__(self):
        return self.title
