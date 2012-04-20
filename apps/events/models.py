import uuid
from hashlib import md5
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import AutoField
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from timezones.fields import TimeZoneField
from entities.models import Entity
from events.managers import EventManager, RegistrantManager, EventTypeManager
from perms.object_perms import ObjectPermission
from perms.models import TendenciBaseModel
from meta.models import Meta as MetaTags
from events.module_meta import EventMeta
from user_groups.models import Group

from invoices.models import Invoice
from files.models import File
from site_settings.utils import get_setting
from payments.models import PaymentMethod as GlobalPaymentMethod

from events.settings import (FIELD_MAX_LENGTH, 
                             LABEL_MAX_LENGTH, 
                             FIELD_TYPE_CHOICES, 
                             USER_FIELD_CHOICES)
from base.utils import localize_date



class TypeColorSet(models.Model):
    """
    Colors representing a type [color-scheme]
    The values can be hex or literal color names
    """
    fg_color = models.CharField(max_length=20)
    bg_color = models.CharField(max_length=20)
    border_color = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s #%s' % (self.pk, self.bg_color)


class Type(models.Model):

    """
    Types is a way of grouping events
    An event can only be one type
    A type can have multiple events
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, editable=False)
    color_set = models.ForeignKey('TypeColorSet')

    objects = EventTypeManager()

    @property
    def fg_color(self):
        return '#%s' % self.color_set.fg_color

    @property
    def bg_color(self):
        return '#%s' % self.color_set.bg_color

    @property
    def border_color(self):
        return '#%s' % self.color_set.border_color

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Type, self).save(*args, **kwargs)


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

    def __unicode__(self):
        str_place = '%s %s %s %s %s' % (
            self.name, self.address, ', '.join(self.city_state()), self.zip, self.country)
        return unicode(str_place.strip())

    def city_state(self):
        return [s for s in (self.city, self.state) if s]


class Registrant(models.Model):
    """
    Event registrant.
    An event can have multiple registrants.
    A registrant can go to multiple events.
    A registrant is static information.
    The names do not change nor does their information
    This is the information that was used while registering
    """
    registration = models.ForeignKey('Registration')
    user = models.ForeignKey(User, blank=True, null=True)
    amount = models.DecimalField(_('Amount'), max_digits=21, decimal_places=2, blank=True, default=0)
    # this is a field used for dynamic pricing registrations only
    pricing = models.ForeignKey('RegConfPricing', null=True)
    
    custom_reg_form_entry = models.ForeignKey("CustomRegFormEntry", 
                                              related_name="registrants", 
                                              null=True)
    
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mail_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=50)
    country = models.CharField(max_length=100)

    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    groups = models.CharField(max_length=100)

    position_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)

    cancel_dt = models.DateTimeField(editable=False, null=True)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    objects = RegistrantManager()

    class Meta:
        permissions = (("view_registrant", "Can view registrant"),)

    def __unicode__(self):
        if self.custom_reg_form_entry:
            return self.custom_reg_form_entry.get_lastname_firstname()
        else:
            return '%s, %s' % (self.last_name, self.first_name)

    @property
    def lastname_firstname(self):
        fn = self.first_name or None
        ln = self.last_name or None
        
        if fn and ln:
            return ', '.join([ln, fn])
        return fn or ln

    @classmethod
    def event_registrants(cls, event=None):

        return cls.objects.filter(
            registration__event=event,
            cancel_dt=None,
        )
        
    @property
    def additional_registrants(self):
        # additional registrants on the same invoice
        return self.registration.registrant_set.filter(cancel_dt=None).exclude(id=self.id).order_by('id')

    @property
    def hash(self):
        return md5(".".join([str(self.registration.event.pk), str(self.pk)])).hexdigest()

    @property
    def old_hash1(self):
        """
        Deprecated: Remove after 7/01/2011
        """
        return md5(".".join([str(self.registration.event.pk), self.email, str(self.pk)])).hexdigest()

    @property
    def old_hash2(self):
        """
        Deprecated: Remove after 7/01/2011
        """
        return md5(".".join([str(self.registration.event.pk), self.email])).hexdigest()

    @models.permalink
    def hash_url(self):
        return ('event.registration_confirmation', [self.registration.event.pk, self.hash])

    @models.permalink
    def get_absolute_url(self):
        return ('event.registration_confirmation', [self.registration.event.pk, self.pk])

    def reg8n_status(self):
        """
        Returns string status.
        """
        config = self.registration.event.registration_configuration

        balance = self.registration.invoice.balance
        payment_required = config.payment_required

        if self.cancel_dt:
            return 'cancelled'

        if balance > 0:
            if payment_required:
                return 'payment-required'
            else:
                return 'registered-with-balance'
        else:
            return 'registered'
        
    def assign_mapped_fields(self):
        """
        Assign the value of the mapped fields from custom registration form to this registrant
        """
        if self.custom_reg_form_entry:
            user_fields = [item[0] for item in USER_FIELD_CHOICES]
            for field in user_fields:
                setattr(self, 'field', self.custom_reg_form_entry.get_value_of_mapped_field(field))
                
            self.name = ('%s %s' % (self.first_name, self.last_name)).strip()


class RegistrationConfiguration(models.Model):
    """
    Event registration
    Extends the event model
    """
    # TODO: use shorter name
    # TODO: do not use fixtures, use RAWSQL to prepopulate
    # TODO: set widget here instead of within form class
    payment_method = models.ManyToManyField(GlobalPaymentMethod)
    payment_required = models.BooleanField(help_text='A payment required before registration is accepted.')
    
    limit = models.IntegerField(_('Registration Limit'), default=0)
    enabled = models.BooleanField(_('Enable Registration'), default=False)

    is_guest_price = models.BooleanField(_('Guests Pay Registrant Price'), default=False)
    
    # custom reg form
    use_custom_reg_form = models.BooleanField(_('Use Custom Registration Form'), default=False)
    reg_form = models.ForeignKey("CustomRegForm", blank=True, null=True, 
                                 verbose_name=_("Custom Registration Form"),
                                 related_name='regconfs',
                                 help_text="You'll have the chance to edit the selected form")
    # a custom reg form can be bound to either RegistrationConfiguration or RegConfPricing
    bind_reg_form_to_conf_only = models.BooleanField(_(' '),
                                 choices=((True, 'Use one form for all pricings'), 
                                          (False, 'Use separate form for each pricing')),
                                 default=True)

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    @property
    def can_pay_online(self):
        """
        Check online payment dependencies.
        Return boolean.
        """
        has_method = GlobalPaymentMethod.objects.filter(is_online=True).exists()
        has_account = get_setting('site', 'global', 'merchantaccount') is not ''
        has_api = settings.MERCHANT_LOGIN is not ''

        return all([has_method, has_account, has_api])


class RegConfPricing(models.Model):
    """
    Registration configuration pricing
    """
    reg_conf = models.ForeignKey(RegistrationConfiguration, blank=True, null=True)
    
    title = models.CharField(max_length=50, blank=True)
    quantity = models.IntegerField(_('Number of attendees'), default=1, blank=True, help_text='Total people included in each registration for this pricing group. Ex: Table or Team.')
    group = models.ForeignKey(Group, blank=True, null=True)
    
    price = models.DecimalField(_('Price'), max_digits=21, decimal_places=2, default=0)
    
    reg_form = models.ForeignKey("CustomRegForm", blank=True, null=True, 
                                 verbose_name=_("Custom Registration Form"),
                                 related_name='regconfpricings',
                                 help_text="You'll have the chance to edit the selected form")
    
    start_dt = models.DateTimeField(_('Start Date'), default=datetime.now())
    end_dt = models.DateTimeField(_('End Date'), default=datetime.now() + timedelta(hours=6))
    
    allow_anonymous = models.BooleanField(_("Public can use"))
    allow_user = models.BooleanField(_("Signed in user can use"))
    allow_member = models.BooleanField(_("All members can use"))
    
    status = models.BooleanField(default=True)
    
    def delete(self, *args, **kwargs):
        """
        Note that the delete() method for an object is not necessarily
        called when deleting objects in bulk using a QuerySet.
        """
        #print "%s, %s" % (self, "status set to false" )
        self.status = False
        self.save(*args, **kwargs)
    
    def __unicode__(self):
        if self.title:
            return '%s' % self.title
        return '%s' % self.pk

    def available(self):
        if not self.reg_conf.enabled or not self.status:
            return False
        if hasattr(self, 'event'):
            if localize_date(datetime.now()) > localize_date(self.event.end_dt, from_tz=self.timezone):
                return False
        return True
    
    @property
    def registration_has_started(self):
        if localize_date(datetime.now()) >= localize_date(self.start_dt, from_tz=self.timezone):
            return True
        return False
        
    @property
    def registration_has_ended(self):
        if localize_date(datetime.now()) >= localize_date(self.end_dt, from_tz=self.timezone):
            return True
        return False
    
    @property
    def is_open(self):
        status = [
            self.reg_conf.enabled,
            self.within_time,
        ]
        return all(status)
    
    @property
    def within_time(self):
        if localize_date(self.start_dt, from_tz=self.timezone) \
            <= localize_date(datetime.now())                    \
            <= localize_date(self.end_dt, from_tz=self.timezone):
            return True
        return False
    
    @property
    def timezone(self):
        return self.reg_conf.event.timezone.zone
    
class Registration(models.Model):

    guid = models.TextField(max_length=40, editable=False)
    note = models.TextField(blank=True)
    event = models.ForeignKey('Event')
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    
    # This field will not be used if dynamic pricings are enabled for registration
    # The pricings should then be found in the Registrant instances
    reg_conf_price = models.ForeignKey(RegConfPricing, null=True)
    
    reminder = models.BooleanField(default=False)
    
    # TODO: Payment-Method must be soft-deleted
    # so that it may always be referenced
    payment_method = models.ForeignKey(GlobalPaymentMethod, null=True)
    amount_paid = models.DecimalField(_('Amount Paid'), max_digits=21, decimal_places=2)

    creator = models.ForeignKey(User, related_name='created_registrations', null=True)
    owner = models.ForeignKey(User, related_name='owned_registrations', null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (("view_registration","Can view registration"),)

    def __unicode__(self):
        return 'Registration - %s' % self.event.title

    @property
    def hash(self):
        return md5(".".join([str(self.event.pk), str(self.pk)])).hexdigest()

    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        """
        description = 'Tendenci Invoice %d for Event (%d): %s - %s (Reg# %d).' % (
            inv.id,
            self.event.pk,
            self.event.title,
            self.event.start_dt.strftime('%Y-%m-%d'),
            inv.object_id,
        )
        
        #The discount used will be the same for all discount uses in one
        #invoice.
        discounts = inv.discountuse_set.filter(invoice=inv)
        if discounts:
            discount = discounts[0].discount.value * discounts.count()
            description += "\nYour discount of $ %s has been added." % discount
        
        return description
        
        
    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the event sale
        """
        from accountings.models import Acct, AcctEntry, AcctTran
        from accountings.utils import make_acct_entries_initial, make_acct_entries_closing
        
        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)
            
            # #CREDIT event SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount*(-1))
    
    # to lookup for the number, go to /accountings/account_numbers/        
    def get_acct_number(self, discount=False):
        if discount:
            return 462000
        else:
            return 402000

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """
        from datetime import datetime
        try:
            from notification import models as notification
        except:
            notification = None
        from perms.utils import get_notice_recipients
        from events.utils import email_admins

        site_label = get_setting('site', 'global', 'sitedisplayname')
        site_url = get_setting('site', 'global', 'siteurl')
        self_reg8n = get_setting('module', 'users', 'selfregistration')

        payment_attempts = self.invoice.payment_set.count()

        registrants = self.registrant_set.all().order_by('id')
        for registrant in registrants:
            #registrant.assign_mapped_fields()
            if registrant.custom_reg_form_entry:
                registrant.name = registrant.custom_reg_form_entry.__unicode__()
            else:
                registrant.name = ' '.join([registrant.first_name, registrant.last_name])

        # only send email on success! or first fail
        if payment.is_paid or payment_attempts <= 1:
            notification.send_emails(
                [self.registrant.email],  # recipient(s)
                'event_registration_confirmation',  # template
                {
                    'SITE_GLOBAL_SITEDISPLAYNAME': site_label,
                    'SITE_GLOBAL_SITEURL': site_url,
                    'site_label': site_label,
                    'site_url': site_url,
                    'self_reg8n': self_reg8n,
                    'reg8n': self,
                    'registrants': registrants,
                    'event': self.event,
                    'price': self.invoice.total,
                    'is_paid': payment.is_paid,
                },
                True,  # notice saved in db
            )
            #notify the admins too
            email_admins(self.event, self.invoice.total, self_reg8n, self, registrants)

    @property
    def canceled(self):
        """
        Return True if all registrants are canceled. Otherwise False.
        """
        registrants = self.registrant_set.all()
        for registrant in registrants:
            if not registrant.cancel_dt:
                return False
        return True

    def status(self):
        """
        Returns registration status.
        """
        config = self.event.registration_configuration

        balance = self.invoice.balance
        payment_required = config.payment_required

        if self.canceled:
            return 'cancelled'

        if balance > 0:
            if payment_required:
                return 'payment-required'
            else:
                return 'registered-with-balance'
        else:
            return 'registered'

    @property
    def registrant(self):
        """
        Gets primary registrant.
        Get first registrant w/ email address
        Order by insertion (primary key)
        """
        registrant = None
        
        if self.event.registration_configuration.use_custom_reg_form:
            registrants = self.registrant_set.all().order_by("pk")
            for reg in registrants:
                if reg.custom_reg_form_entry:
                    email = reg.custom_reg_form_entry.get_email()
                    if email:
                        registrant = reg
                        registrant.email = email
                        break
            if (not registrant) and registrants:
                # this registrant probably didn't use the custom reg form,
                # but the custom reg form is now enabled
                registrant = registrants[0]
                
        else:
            try:
                registrant = self.registrant_set.filter(
                    email__isnull=False).order_by("pk")[0]
            except:
                pass

        return registrant

    def save(self, *args, **kwargs):
        if not self.pk:
            self.guid = str(uuid.uuid1())
        super(Registration, self).save(*args, **kwargs)

    def save_invoice(self, *args, **kwargs):
        status_detail = kwargs.get('status_detail', 'tendered')
        admin_notes = kwargs.get('admin_notes', None)
        
        object_type = ContentType.objects.get(app_label=self._meta.app_label, 
            model=self._meta.module_name)

        try: # get invoice
            invoice = Invoice.objects.get(
                object_type = object_type,
                object_id = self.pk,
            )
        except ObjectDoesNotExist: # else; create invoice
            # cannot use get_or_create method
            # because too many fields are required
            invoice = Invoice()
            invoice.object_type = object_type
            invoice.object_id = self.pk

        # update invoice with details
        invoice.title = "Registration %s for Event: %s" % (self.pk, self.event.title)
        invoice.estimate = True
        invoice.status_detail = status_detail
        invoice.subtotal = self.amount_paid
        invoice.total = self.amount_paid
        invoice.balance = invoice.total
        invoice.tender_date = datetime.now()
        invoice.due_date = datetime.now()
        invoice.ship_date = datetime.now()
        invoice.admin_notes = admin_notes
        invoice.save()

        self.invoice = invoice

        self.save()

        return invoice


class Payment(models.Model):
    """
    Event registration payment
    Extends the registration model
    """
    registration = models.OneToOneField('Registration')


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

    def __unicode__(self):
        return self.name


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

    def __unicode__(self):
        return self.name

    def files(self):
        return File.objects.get_for_model(self)

    def get_photo(self):

        if hasattr(self,'cached_photo'):
            return self.cached_photo

        files = File.objects.get_for_model(self).order_by('-update_dt')
        photos = [f for f in files if f.type() == 'image']

        photo = None
        if photos:
            photo = photos[0]  # most recent
            self.cached_photo = photo

        return photo


class Event(TendenciBaseModel):
    """
    Calendar Event
    """
    guid = models.CharField(max_length=40, editable=False)
    entity = models.ForeignKey(Entity, blank=True, null=True)

    type = models.ForeignKey(Type, blank=True, null=True)

    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    all_day = models.BooleanField()
    start_dt = models.DateTimeField(default=datetime.now())
    end_dt = models.DateTimeField(default=datetime.now()+timedelta(hours=2))
    timezone = TimeZoneField(_('Time Zone'))

    place = models.ForeignKey('Place', null=True)
    registration_configuration = models.OneToOneField('RegistrationConfiguration', null=True, editable=False)

    private = models.BooleanField() # hide from lists
    password = models.CharField(max_length=50, blank=True)
    
    on_weekend = models.BooleanField(default=True, help_text=_("This event occurs on weekends"))
    
    external_url = models.URLField(_('External URL'), default=u'', blank=True)
    image = models.ForeignKey('EventPhoto', 
        help_text=_('Photo that represents this event.'), null=True, blank=True)
        
    tags = TagField(blank=True)
    
    # html-meta tags
    meta = models.OneToOneField(MetaTags, null=True)

    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = EventManager()

    class Meta:
        permissions = (("view_event","Can view event"),)

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        methods coupled to this instance.
        """
        return EventMeta().get_meta(self, name)

    def is_registrant(self, user):
        return Registration.objects.filter(event=self, registrant=user).exists()

    @models.permalink
    def get_absolute_url(self):
        return ("event", [self.pk])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.guid = str(uuid.uuid1())
        photo_upload = kwargs.pop('photo', None)
        super(Event, self).save(*args, **kwargs)

        if photo_upload and self.pk:
            image = EventPhoto(
                        creator = self.creator,
                        creator_username = self.creator_username,
                        owner = self.owner,
                        owner_username = self.owner_username
                    )

            image.file.save(photo_upload.name, photo_upload)  # save file row
            image.save()  # save image row

            if self.image:
                self.image.delete()  # delete image and file row
            self.image = image  # set image

            self.save()

    def __unicode__(self):
        return self.title

    # this function is to display the event date in a nice way.
    # example format: Thursday, August 12, 2010 8:30 AM - 05:30 PM - GJQ 8/12/2010
    def dt_display(self, format_date='%a, %b %d, %Y', format_time='%I:%M %p'):
        from base.utils import format_datetime_range
        return format_datetime_range(self.start_dt, self.end_dt, format_date, format_time)

    @property
    def is_over(self):
        return self.end_dt <= datetime.now()

    @property
    def money_collected(self):
        """
        Total collected from this event
        """
        total_sum = Registration.objects.filter(event=self).aggregate(
            Sum('invoice__total'),
        )['invoice__total__sum']

        # total_sum is the amount of money received when all is said and done
        return total_sum - self.money_outstanding

    @property
    def money_outstanding(self):
        """
        Outstanding balance for this event
        """
        figures = Registration.objects.filter(event=self).aggregate(
            Sum('invoice__total'),
            Sum('invoice__balance'),
        )
        balance_sum = figures['invoice__balance__sum']
        total_sum = figures['invoice__total__sum']

        return total_sum - balance_sum

    def registrants(self, **kwargs):
        """
        This method can return 3 different values.
        All registrants, registrants with a balance, registrants without a balance.
        This method does not respect permissions.
        """

        registrants = Registrant.objects.filter(registration__event=self, cancel_dt=None)

        if 'with_balance' in kwargs:
            with_balance = kwargs['with_balance']

            if with_balance:
                registrants = registrants.filter(registration__invoice__balance__gt=0)
            else:
                registrants = registrants.filter(registration__invoice__balance__lte=0)

        return registrants
        
    def number_of_days(self):
        delta = self.end_dt - self.start_dt
        return delta.days
    
    @property
    def photo(self):
        if self.image:
            return self.image.file
        return None
    
class CustomRegForm(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    notes = models.TextField(_("Notes"), max_length=2000, blank=True)
    validate_guest = models.BooleanField(_("Validate Guest"), default=False,
                                         help_text="If checked, required fields for " + \
                                         "the primary registrant will also be required for the guests")
    
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="custom_reg_creator", null=True)
    creator_username = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name="custom_reg_owner", null=True)    
    owner_username = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='active')
    
    class Meta:
        verbose_name = _("Custom Registration Form")
        verbose_name_plural = _("Custom Registration Forms")
        
    def __unicode__(self):
        return self.name
    
    @property
    def is_template(self):
        """
        A custom registration form is a template when it is not associated with
        registration configuration and any event registration conf pricing. 
        A form template can be re-used and will be cloned if it is selected by
        a regconf or an regconfpricing.
        """
        if self.regconfs.exists() or self.regconfpricings.exists():
            return False
        return True
    
    def clone(self):
        """
        Clone this custom registration form and associate it with the event if provided.
        """
        params = dict([(field.name, getattr(self, field.name)) \
                       for field in self._meta.fields if not field.__class__==AutoField])
        cloned_obj = self.__class__.objects.create(**params)
        # clone fiellds
        fields = self.fields.all()
        for field in fields:
            field.clone(form=cloned_obj)
            
        return cloned_obj
    

class CustomRegField(models.Model):
    form = models.ForeignKey("CustomRegForm", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    map_to_field = models.CharField(_("Map to User Field"), choices=USER_FIELD_CHOICES,
        max_length=64, blank=True, null=True)
    field_type = models.CharField(_("Type"), choices=FIELD_TYPE_CHOICES,
        max_length=64)
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
        help_text="Comma separated options where applicable")
    position = models.PositiveIntegerField(_('position'), default=0)
    default = models.CharField(_("Default"), max_length=1000, blank=True,
        help_text="Default value of the field")
    display_on_roster = models.BooleanField(_("Show on Roster"), default=False)
    
    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        ordering = ('position',)
        
    def clone(self, form=None):
        """
        Clone this custom registration field, and associate it with the form if provided.
        """
        params = dict([(field.name, getattr(self, field.name)) \
                       for field in self._meta.fields if not field.__class__==AutoField])
        cloned_field = self.__class__.objects.create(**params)
        
        if form:
            cloned_field.form = form
            cloned_field.save()
        return cloned_field
        
                
class CustomRegFormEntry(models.Model):
    form = models.ForeignKey("CustomRegForm", related_name="entries")
    entry_time = models.DateTimeField(_("Date/time"))
    
    def __unicode__(self):
        name = self.get_name()
        if name:
            return name
        
        # top 2 fields
        values = []
        top_fields = CustomRegField.objects.filter(form=self.form,
                                                   field_type='CharField'
                                                   ).order_by('position')[0:2]
        for field in top_fields:
            field_entries = field.entries.filter(entry=self)
            if field_entries:
                values.append(field_entries[0].value)
        return (' '.join(values)).strip()
    
    def get_value_of_mapped_field(self, map_to_field):
        mapped_field = CustomRegField.objects.filter(form=self.form,
                                map_to_field=map_to_field)
        if mapped_field:
            #field_entries = CustomRegFieldEntry.objects.filter(entry=self, field=mapped_field[0])
            field_entries = mapped_field[0].entries.filter(entry=self)
            if field_entries:
                return (field_entries[0].value).strip()
        return ''

    
    def get_name(self):
        name = ' '.join([self.get_value_of_mapped_field('first_name'), 
                         self.get_value_of_mapped_field('last_name')])
        return name.strip()

    def get_lastname_firstname(self):
        name = '%s, %s' % (self.get_value_of_mapped_field('last_name'), 
                         self.get_value_of_mapped_field('first_name'))
        return name.strip()

    
    def get_email(self):
        return self.get_value_of_mapped_field('email')
    
    def get_field_entry_list(self):
        field_entries = self.field_entries.order_by('field')
        entry_list = []
        for field_entry in field_entries:
            entry_list.append({'label': field_entry.field.label, 'value': field_entry.value})
        return entry_list
    
    def get_non_mapped_field_entry_list(self):
        field_entries = self.field_entries
        mapped_fields = [item[0] for item in USER_FIELD_CHOICES]
        field_entries = field_entries.exclude(field__map_to_field__in=mapped_fields).order_by('field')
        entry_list = []
        for field_entry in field_entries:
            entry_list.append({'label': field_entry.field.label, 'value': field_entry.value})
        return entry_list
            
    
    def roster_field_entry_list(self):
        list_on_roster = []
        field_entries = self.field_entries.exclude(field__map_to_field__in=[
                                    'first_name', 
                                    'last_name', 
                                    'position_title', 
                                    'company_name'
                                    ]).filter(field__display_on_roster=1).order_by('field')

        for field_entry in field_entries:
            list_on_roster.append({'label': field_entry.field.label, 'value': field_entry.value})
        return list_on_roster
        

class CustomRegFieldEntry(models.Model):
    entry = models.ForeignKey("CustomRegFormEntry", related_name="field_entries")
    field = models.ForeignKey("CustomRegField", related_name="entries")
    value = models.CharField(max_length=FIELD_MAX_LENGTH)

class EventPhoto(File):
    @property
    def content_type(self):
        return 'events'


class Addon(models.Model):
    event = models.ForeignKey(Event)
    title = models.CharField(max_length=50)
    price = models.DecimalField(_('Price'), max_digits=21, decimal_places=2, default=0)
    
    # permission fields
    group = models.ForeignKey(Group, blank=True, null=True)
    allow_anonymous = models.BooleanField(_("Public can use"))
    allow_user = models.BooleanField(_("Signed in user can use"))
    allow_member = models.BooleanField(_("All members can use"))
    
    status = models.BooleanField(default=True)
    
    def delete(self, *args, **kwargs):
        """
        Note that the delete() method for an object is not necessarily
        called when deleting objects in bulk using a QuerySet.
        """
        #print "%s, %s" % (self, "status set to false" )
        self.status = False
        self.save(*args, **kwargs)
    
    def __unicode__(self):
        return self.title

    def available(self):
        if not self.reg_conf.enabled or not self.status:
            return False
        if hasattr(self, 'event'):
            if datetime.now() > self.event.end_dt:
                return False
        return True
    
    def field_name(self):
        return "%s_%s" % (self.pk, self.title.lower().replace(' ', '').replace('-', ''))
    
class AddonOption(models.Model):
    addon = models.ForeignKey(Addon, related_name="options")
    title = models.CharField(max_length=100)
    # old field for 2 level options (e.g. Option: Size -> Choices: small, large)
    # choices = models.CharField(max_length=200, help_text=_('options are separated by commas, ex: option 1, option 2, option 3'))
    
    def __unicode__(self):
        return self.title

            
class RegAddon(models.Model):
    """Event registration addon.
    An event registration can avail multiple addons.
    This stores the addon's price at the time of registration.
    This stores the user's selected options for the addon.
    """
    registration = models.ForeignKey('Registration')
    addon = models.ForeignKey('Addon')
    
    # price at the moment of registration
    amount = models.DecimalField(_('Amount'), max_digits=21, decimal_places=2, default=0)
    
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "%s: %s" % (self.registration.pk, self.addon.title)
    
class RegAddonOption(models.Model):
    """Selected event registration addon option.
    """
    regaddon = models.ForeignKey(RegAddon)
    option = models.ForeignKey(AddonOption)
    # old field for 2 level options (e.g. Option: Size -> Choices: small, large)
    # selected_option = models.CharField(max_length=50)
    
    class Meta:
        unique_together = (('regaddon', 'option'),)
        
    def __unicode__(self):
        return "%s: %s - %s" % (self.regaddon.pk, self.option.title, self.selected_option)
    
