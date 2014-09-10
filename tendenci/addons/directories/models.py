import uuid
import re
from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser

from tagging.fields import TagField
from timezones.fields import TimeZoneField
from tinymce import models as tinymce_models
from tendenci.core.meta.models import Meta as MetaTags
from tendenci.core.base.fields import SlugField
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.categories.models import CategoryItem
from tendenci.apps.invoices.models import Invoice
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.files.models import File
from tendenci.addons.directories.module_meta import DirectoryMeta
from tendenci.addons.directories.managers import DirectoryManager
from tendenci.addons.directories.choices import ADMIN_DURATION_CHOICES
from tendenci.libs.boto_s3.utils import set_s3_file_permission


def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    return 'directories/%d/%s' % (instance.id, filename)

class Directory(TendenciBaseModel):

    guid = models.CharField(max_length=40)
    slug = SlugField(_('URL Path'), unique=True)
    timezone = TimeZoneField(_('Time Zone'))
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    body = tinymce_models.HTMLField()
    source = models.CharField(max_length=300, blank=True)
    # logo = models.FileField(max_length=260, upload_to=file_directory,
    #                         help_text=_('Company logo. Only jpg, gif, or png images.'),
    #                         blank=True)

    logo_file = models.ForeignKey(File, null=True)

    first_name = models.CharField(_('First Name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=100, blank=True)
    address = models.CharField(_('Address'), max_length=100, blank=True)
    address2 = models.CharField(_('Address 2'), max_length=100, blank=True)
    city = models.CharField(_('City'), max_length=50, blank=True)
    state = models.CharField(_('State'), max_length=50, blank=True)
    zip_code = models.CharField(_('Zip Code'), max_length=50, blank=True)
    country = models.CharField(_('Country'), max_length=50, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    phone2 = models.CharField(_('Phone 2'), max_length=50, blank=True)
    fax = models.CharField(_('Fax'), max_length=50, blank=True)
    email = models.CharField(_('Email'), max_length=120, blank=True)
    email2 = models.CharField(_('Email 2'), max_length=120, blank=True)
    website = models.CharField(max_length=300, blank=True)

    renewal_notice_sent = models.BooleanField(default=False)
    list_type = models.CharField(_('List Type'), max_length=50, blank=True)
    requested_duration = models.IntegerField(_('Requested Duration'), default=0)
    pricing = models.ForeignKey('DirectoryPricing', null=True)
    activation_dt = models.DateTimeField(_('Activation Date/Time'), null=True, blank=True)
    expiration_dt = models.DateTimeField(_('Expiration Date/Time'), null=True, blank=True)
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    payment_method = models.CharField(_('Payment Method'), max_length=50, blank=True)

    syndicate = models.BooleanField(_('Include in RSS feed'), default=True)
    design_notes = models.TextField(_('Design Notes'), blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)
    tags = TagField(blank=True)

    # for podcast feeds
    enclosure_url = models.CharField(_('Enclosure URL'), max_length=500, blank=True)
    enclosure_type = models.CharField(_('Enclosure Type'), max_length=120, blank=True)
    enclosure_length = models.IntegerField(_('Enclosure Length'), default=0)

    # html-meta tags
    meta = models.OneToOneField(MetaTags, null=True)

    categories = generic.GenericRelation(CategoryItem,
                                          object_id_field="object_id",
                                          content_type_field="content_type")
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = DirectoryManager()

    class Meta:
        permissions = (("view_directory",_("Can view directory")),)
        verbose_name = _("Directory")
        verbose_name_plural = _("Directories")

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        methods coupled to this instance.
        """
        return DirectoryMeta().get_meta(self, name)

    @models.permalink
    def get_absolute_url(self):
        return ("directory", [self.slug])

    @models.permalink
    def get_renew_url(self):
        return ("directory.renew", [self.id])

    def __unicode__(self):
        return self.headline

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())

        super(Directory, self).save(*args, **kwargs)
        if self.logo:
            if self.is_public():
                set_s3_file_permission(self.logo.name, public=True)
            else:
                set_s3_file_permission(self.logo.name, public=False)

    def is_public(self):
        return all([self.allow_anonymous_view,
                self.status,
                self.status_detail in ['active']])

    @property
    def logo(self):
        """
        This represents the logo FileField

        Originally this was a FileField, but later
        we added the attribute logo_file to leverage
        the File model.  We then replaced the logo
        property with this convience method for
        backwards compatibility.
        """
        if self.logo_file:
            return self.logo_file.file

    def get_logo_url(self):
        if not self.logo_file:
            return u''

        return reverse('file', args=[self.logo_file.pk])

    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        """
        return 'Tendenci Invoice %d for Directory: %s (%d).' % (
            inv.id,
            self.headline,
            inv.object_id,
        )

    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the directory sale
        """
        from tendenci.apps.accountings.models import Acct, AcctEntry, AcctTran
        from tendenci.apps.accountings.utils import make_acct_entries_initial, make_acct_entries_closing

        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)

            # #CREDIT directory SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount*(-1))

    def get_acct_number(self, discount=False):
        if discount:
            return 464400
        else:
            return 404400

    def auto_update_paid_object(self, request, payment):
        """
        Update the object after online payment is received.
        """
        if not request.user.profile.is_superuser:
            self.status_detail = 'paid - pending approval'
            self.save()

    def age(self):
        return datetime.now() - self.create_dt

    @property
    def category_set(self):
        items = {}
        for cat in self.categories.select_related('category__name', 'parent__name'):
            if cat.category:
                items["category"] = cat.category
            elif cat.parent:
                items["sub_category"] = cat.parent
        return items

    def renew_window(self):
        days = get_setting('module', 'directories', 'renewaldays')
        days = int(days)
        if datetime.now() + timedelta(days) > self.expiration_dt:
            return True
        else:
            return False

class DirectoryPricing(models.Model):
    guid = models.CharField(max_length=40)
    duration = models.IntegerField(blank=True, choices=ADMIN_DURATION_CHOICES)
    regular_price =models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    premium_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    regular_price_member = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    premium_price_member = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    show_member_pricing = models.BooleanField()
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name="directory_pricing_creator",  null=True, on_delete=models.SET_NULL)
    creator_username = models.CharField(max_length=50, null=True)
    owner = models.ForeignKey(User, related_name="directory_pricing_owner", null=True, on_delete=models.SET_NULL)
    owner_username = models.CharField(max_length=50, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        permissions = (("view_directorypricing", _("Can view directory pricing")),)

    def __unicode__(self):
        currency_symbol = get_setting('site', 'global', 'currencysymbol')
        price = "%s%s(R)/%s(P)" % (currency_symbol, self.regular_price, self.premium_price)
        return "%d days for %s" % (self.duration, price)

    def save(self, user=None, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
            if user and user.id:
                self.creator=user
                self.creator_username=user.username
        if user and user.id:
            self.owner=user
            self.owner_username=user.username
        if not self.regular_price: self.regular_price = 0
        if not self.premium_price: self.premium_price = 0

        super(DirectoryPricing, self).save(*args, **kwargs)

    def get_price_for_user(self, user=AnonymousUser(), list_type='regular'):
        if not user.is_anonymous() and user.profile.is_member:
            if list_type == 'regular':
                return self.regular_price_member
            else:
                return self.premium_price_member
        else:
            if list_type == 'regular':
                return self.regular_price
            else:
                return self.premium_price

