import uuid
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.signals import post_save

from tendenci.apps.perms.utils import has_perm
from tendenci.apps.invoices.managers import InvoiceManager
from tendenci.apps.invoices.listeners import update_profiles_total_spend
from tendenci.apps.accountings.utils import (make_acct_entries,
                                    make_acct_entries_reversing)
from tendenci.apps.entities.models import Entity

STATUS_DETAIL_CHOICES = (
    ('estimate', _('Estimate')),
    ('tendered', _('Tendered')))

class Invoice(models.Model):
    guid = models.CharField(max_length=50)

    object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.IntegerField(default=0, blank=True, null=True)
    _object = GenericForeignKey('object_type', 'object_id')
    title = models.CharField(max_length=200, blank=True, null=True)
    creator = models.ForeignKey(User, related_name="invoice_creator", null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="invoice_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    entity = models.ForeignKey(Entity, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name="invoices")
    create_dt = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    update_dt = models.DateTimeField(auto_now=True)
    tender_date = models.DateTimeField(null=True)
    arrival_date_time = models.DateTimeField(blank=True, null=True)
    is_void = models.BooleanField(default=False)
    status_detail = models.CharField(max_length=50, choices=STATUS_DETAIL_CHOICES, default='estimate')
    status = models.BooleanField(default=True)
    payments_credits = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    discount_code = models.CharField(_('Discount Code'), max_length=100, blank=True, null=True)
    discount_amount = models.DecimalField(_('Discount Amount'), max_digits=10, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    variance_notes = models.TextField(max_length=1000, blank=True, null=True)
    receipt = models.BooleanField(default=False)
    gift = models.BooleanField(default=False)
    greeting = models.CharField(max_length=500, blank=True, null=True)
    instructions = models.CharField(max_length=500, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True)
    terms = models.CharField(max_length=50, blank=True)
    disclaimer = models.CharField(max_length=150, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    fob = models.CharField(max_length=50, blank=True, null=True)
    project = models.CharField(max_length=50, blank=True, null=True)
    other = models.CharField(max_length=120, blank=True, null=True)
    message = models.CharField(max_length=150, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    tax_exempt = models.BooleanField(default=True)
    tax_exemptid = models.CharField(max_length=50, blank=True, null=True)
    tax_rate = models.FloatField(blank=True, default=0)
    taxable = models.BooleanField(default=False)
    tax = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    bill_to = models.CharField(max_length=120, blank=True)
    bill_to_first_name = models.CharField(max_length=100, blank=True, null=True)
    bill_to_last_name = models.CharField(max_length=100, blank=True, null=True)
    bill_to_company = models.CharField(max_length=100, blank=True, null=True)
    bill_to_address = models.CharField(max_length=250, blank=True, null=True)
    bill_to_city = models.CharField(max_length=50, blank=True, null=True)
    bill_to_state = models.CharField(max_length=50, blank=True, null=True)
    bill_to_zip_code = models.CharField(max_length=20, blank=True, null=True)
    bill_to_country = models.CharField(max_length=255, blank=True, null=True)
    bill_to_phone = models.CharField(max_length=50, blank=True, null=True)
    bill_to_fax = models.CharField(max_length=50, blank=True, null=True)
    bill_to_email = models.CharField(max_length=100, blank=True, null=True)
    ship_to = models.CharField(max_length=120, blank=True)
    ship_to_first_name = models.CharField(max_length=50, blank=True)
    ship_to_last_name = models.CharField(max_length=50, blank=True)
    ship_to_company = models.CharField(max_length=100, blank=True)
    ship_to_address = models.CharField(max_length=250, blank=True)
    ship_to_city = models.CharField(max_length=50, blank=True)
    ship_to_state = models.CharField(max_length=50, blank=True)
    ship_to_zip_code = models.CharField(max_length=20, blank=True)
    ship_to_country = models.CharField(max_length=255, blank=True)
    ship_to_phone = models.CharField(max_length=50, blank=True, null=True)
    ship_to_fax = models.CharField(max_length=50, blank=True, null=True)
    ship_to_email = models.CharField(max_length=100, blank=True, null=True)
    ship_to_address_type = models.CharField(max_length=50, blank=True, null=True)
    ship_date = models.DateTimeField()
    ship_via = models.CharField(max_length=50, blank=True)
    shipping = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipping_surcharge = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    box_and_packing = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    objects = InvoiceManager()

    class Meta:
        permissions = (("view_invoice", _("Can view invoice")), )
        app_label = 'invoices'

    def __unicode__(self):
        return "Invoice %s" % self.pk

    def set_creator(self, user):
        """
        Sets creator fields.
        """
        self.creator = user
        self.creator_username = user.username

    def set_owner(self, user):
        """
        Sets owner fields.
        """
        self.owner = user
        self.owner_username = user.username

    def bill_to_user(self, user):
        """
        This method populates all of the ship to fields
        via info in user and user.profile object.
        """
        self.bill_to = '%s %s' % (user.first_name, user.last_name)
        self.bill_to = self.bill_to.strip()

        self.bill_to_first_name = user.first_name
        self.bill_to_last_name = user.last_name
        self.bill_to_email = user.email

        if hasattr(user, 'profile'):
            self.bill_to_company = user.profile.company
            self.bill_to_address = user.profile.address
            self.bill_to_city = user.profile.city
            self.bill_to_state = user.profile.state
            self.bill_to_zip_code = user.profile.zipcode
            self.bill_to_country = user.profile.country
            self.bill_to_phone = user.profile.phone
            self.bill_to_fax = user.profile.fax

    def ship_to_user(self, user):
        """
        This method populates all of the ship to fields
        via info in user and user.profile object.
        """
        self.bill_to = '%s %s' % (user.first_name, user.last_name)
        self.ship_to = self.ship_to.strip()

        self.ship_to_first_name = user.first_name
        self.ship_to_last_name = user.last_name
        self.ship_to_email = user.email

        if hasattr(user, 'profile'):
            self.ship_to_company = user.profile.company
            self.ship_to_address = user.profile.address
            self.ship_to_city = user.profile.city
            self.ship_to_state = user.profile.state
            self.ship_to_zip_code = user.profile.zipcode
            self.ship_to_country = user.profile.country
            self.ship_to_phone = user.profile.phone
            self.ship_to_fax = user.profile.fax
            self.ship_to_address_type = user.profile.address_type

    def split_title(self):
        if ": " in self.title:
            split_title = ': '.join(self.title.split(': ')[1:])
            return u'%s' % split_title
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('invoice.view', [self.id])

    @models.permalink
    def get_absolute_url_with_guid(self):
        return ('invoice.view', [self.id, self.guid])

    @models.permalink
    def get_discount_url(self):
        from tendenci.apps.discounts.models import Discount
        if self.discount_code:
            try:
                discount = Discount.objects.get(discount_code=self.discount_code)
                return ('discount.detail', [discount.id])
            except Discount.DoesNotExist:
                return ''
        return ''

    def save(self, user=None):
        """
        Set guid, creator and owner if any of
        these fields are missing.
        """
        self.guid = self.guid or uuid.uuid1().get_hex()

        if hasattr(user, 'pk') and not user.is_anonymous():
            self.set_creator(user)
            self.set_owner(user)

        # assign entity
        if not self.entity_id and self.object_type:
            self.entity = self.get_entity()

        super(Invoice, self).save()

    def delete(self, *args, **kwargs):
        """
        Invoices are never deleted.
        Per Ed Schipul 06/05/2013
        """
        pass

    def get_entity(self):
        """
        Discover the entity for this invoice.

        Note that - the entity we're looking for is the entity
        from the object's group, not the object's entity field.
        """
        entity = None
        obj = self.get_object()
        if obj:
            # an object is associated with a group which ties to an entity
            group = None
            if hasattr(obj, 'group'):
                group = getattr(obj, 'group')
                if group:
                    entity = group.entity
        if not entity:
            entity = Entity.objects.first()

        return entity

    def get_object(self):
        _object = None
        try:
            _object = self._object
        except:
            pass
        # exclude the soft deleted object - when an object is soft deleted,
        # its slug is appended with "@ + object.pk", which causes error on
        # resolving url (on invoice search and detail pages) because "@"
        # is not valid in the slug url pattern.
        if _object and hasattr(_object, 'status') and (not _object.status):
            _object = None
        return _object

    def get_status(self):
        """
        Return status (string)
        Use status_detail and is_voide attribute
        """
        if self.is_void:
            return u'void'

        return self.status_detail


    @property
    def is_tendered(self):
        boo = False
        if self.id > 0:
            if self.status_detail.lower() == 'tendered':
                boo = True
        return boo

    def tender(self, user):
        """ mark it as tendered if we have records """
        if not self.is_tendered:
            # make accounting entry
            make_acct_entries(user, self, self.total)
            self.status_detail = 'tendered'
            self.status = 1
            self.tender_date = datetime.now()
            self.save()
        return True

    # if this invoice allows view by user2_compare
    def allow_view_by(self, user2_compare, guid=''):
        if user2_compare.profile.is_superuser:
            return True

        if has_perm(user2_compare, 'invoices.view_invoice'):
            return True

        if self.guid == guid:
            return True

        if user2_compare.is_authenticated():
            if user2_compare in [self.creator, self.owner]:
                return self.status

        return False

    def allow_payment_by(self, user2_compare,  guid=''):
        return self.allow_view_by(user2_compare,  guid)

    # if this invoice allows edit by user2_compare
    def allow_edit_by(self, user2_compare, guid=''):
        boo = False
        if user2_compare.is_superuser:
            boo = True
        else:
            if user2_compare and user2_compare.id > 0:
                if has_perm(user2_compare, 'invoices.change_invoice'):
                    return True

                if self.creator == user2_compare or \
                        self.owner == user2_compare:
                    if self.status == 1:
                        # user can only edit a non-tendered invoice
                        if not self.is_tendered:
                            boo = True
            else:
                if self.guid and self.guid == guid:  # for anonymous user
                    if self.status == 1 and not self.is_tendered:
                        boo = True
        return boo

    def make_payment(self, user, amount):
        """
        Updates the invoice balance by adding
        accounting entries.
        """

        if self.is_tendered and self.balance > 0:
            self.balance -= amount
            self.payments_credits += amount
            self.save()

            # Make the accounting entries here
            make_acct_entries(user, self, amount)

            return True

        return False

    def void_payment(self, user, amount):
        self.balance += amount
        self.payments_credits -= amount
        self.save()
        # only void approved and non-zero payments
        for payment in self.payment_set.filter(
                                status_detail='approved',
                                amount__gt=0):
            payment.status_detail = 'void'
            payment.save()

        # reverse accounting entries
        make_acct_entries_reversing(user, self, amount)

    def void(self):
        """
        Voids invoice. This means the debt is no longer owed.
        """
        if not self.is_void:
            self.is_void = True
            self.save()

    def unvoid(self):
        """
        Remove 'void' from invoice. This means the invoice is active again.
        """
        if self.is_void:
            self.is_void = False
            self.save()

    def get_first_approved_payment(self):
        """
        Returns first approved payment in ascending order
        """
        [payment] = self.payment_set.filter(status_detail='approved')[:1] or [None]
        return payment

# add signals
post_save.connect(update_profiles_total_spend, sender=Invoice,
    dispatch_uid='tendenci.apps.invoices.models.update_profiles_total_spend')
