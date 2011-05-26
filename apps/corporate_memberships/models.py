import uuid
from datetime import datetime, timedelta
from django import forms
from django.utils.importlib import import_module
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
#from django.contrib.contenttypes.models import ContentType
from tinymce import models as tinymce_models

#from completion import AutocompleteProvider, site

from perms.models import TendenciBaseModel
from invoices.models import Invoice
from memberships.models import MembershipType, App, Membership
from forms_builder.forms.settings import FIELD_MAX_LENGTH, LABEL_MAX_LENGTH
from corporate_memberships.managers import CorporateMembershipManager
from perms.utils import is_admin
#from site_settings.utils import get_setting

FIELD_CHOICES = (
                    ("CharField", _("Text")),
                    ("CharField/django.forms.Textarea", _("Paragraph Text")),
                    ("BooleanField", _("Checkbox")),
                    ("ChoiceField", _("Select One from a list (Drop Down)")),
                    ("ChoiceField/django.forms.RadioSelect", _("Select One from a list (Radio Buttons)")),
                    ("MultipleChoiceField", _("Multi select (Drop Down)")),
                    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi select (Checkboxes)")),
                    ("EmailField", _("Email")),
                    ("FileField", _("File upload")),
                    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
                    ("DateTimeField", _("Date/time")),
                    ("section_break", _("Section Break")),
                    ("page_break", _("Page Break")),
                )

FIELD_LAYOUT_CHOICES = (
                        ('1', _('One Column')),
                        ('2', _('Two Columns')),
                        ('3', _('Three Columns')),
                        ('0', _('Side by Side')),
                        )
AUTH_METHOD_CHOICES = (
                       ('admin', _('Admin Approval')),
                       ('email', _('E-mail Domain')),
                       ('secret_code', _('Secret Code')),
                       )
SIZE_CHOICES = (
                ('s', _('Small')),
                ('m', _('Medium')),
                ('l', _('Large')),
                )


class CorporateMembershipType(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.CharField(_('Description'), max_length=500)
    price = models.DecimalField(_('Price'), max_digits=15, decimal_places=2, blank=True, default=0,
                                help_text="Set 0 for free membership.")
    renewal_price = models.DecimalField(_('Renewal Price'), max_digits=15, decimal_places=2, 
                                        blank=True, default=0, null=True,
                                        help_text="Set 0 for free membership.")
    membership_type = models.ForeignKey(MembershipType, 
                                        help_text=_("Bind individual memberships to this membership type.")) 
    
    order = models.IntegerField(_('Order'), default=0, 
                                help_text='Types will be displayed in ascending order based on this field.')
    admin_only = models.BooleanField(_('Admin Only'), default=0)  # from allowuseroption
    
    apply_threshold = models.BooleanField(_('Allow Threshold'), default=0)
    individual_threshold = models.IntegerField(_('Threshold Limit'), default=0, blank=True, null=True)
    individual_threshold_price = models.DecimalField(_('Threshold Price'), max_digits=15, 
                                                     decimal_places=2, blank=True, null=True, default=0,
                                                     help_text=_("All individual members applying under or " + \
                                                                 "equal to the threashold limit receive the " + \
                                                                 "threshold prices."))

    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
        
    
class CorporateMembership(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    corporate_membership_type = models.ForeignKey("CorporateMembershipType", verbose_name=_("MembershipType")) 
    name = models.CharField(max_length=250, unique=True)
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, default='', blank=True, null=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zip = models.CharField(_('zipcode'), max_length=50, blank=True, null=True)
    country = models.CharField(_('country'), max_length=50, blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=50, blank=True, null=True)
    email = models.CharField(_('email'), max_length=200,  blank=True, null=True)
    url = models.CharField(_('url'), max_length=100, blank=True, null=True)
    #authorized_domains = models.CharField(max_length=500, blank=True, null=True)
    secret_code = models.CharField(max_length=50, blank=True, null=True)
    
    renewal = models.BooleanField(default=0)
    renew_entry_id = models.IntegerField(default=0, blank=True, null=True) 
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField(_("Join Date Time")) 
    renew_dt = models.DateTimeField(_("Renew Date Time"), null=True) 
    expiration_dt = models.DateTimeField(_("Expiration Date Time"), blank=True, null=True)
    approved = models.BooleanField(_("Approved"), default=0)
    approved_denied_dt = models.DateTimeField(_("Approved or Denied Date Time"), null=True)
    approved_denied_user = models.ForeignKey(User, verbose_name=_("Approved or Denied User"), null=True)
    payment_method = models.CharField(_("Payment Method"), max_length=50)
    
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    
    corp_app = models.ForeignKey("CorpApp")
    
    objects = CorporateMembershipManager()
    
    class Meta:
        permissions = (("view_corporatemembership", "Can view corporate membership"),)
        verbose_name = _("Corporate Membership")
        verbose_name_plural = _("Corporate Memberships")
    
    def __unicode__(self):
        return "%s" % (self.name)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
        
    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        """
        return 'Tendenci Invoice %d for Corp. Memb. (%d): %s. ' % (
            inv.id,
            inv.object_id,
            self.name,
        )
        
    def make_acct_entries(self, user, inv, amount, **kwargs):
        """
        Make the accounting entries for the corporate membership sale
        """
        from accountings.models import Acct, AcctEntry, AcctTran
        from accountings.utils import make_acct_entries_initial, make_acct_entries_closing
        
        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', inv.id)
        if not inv.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            # payment has now been received
            make_acct_entries_closing(user, ae, amount)
            
            # #CREDIT corporate membership SALES
            acct_number = self.get_acct_number()
            acct = Acct.objects.get(account_number=acct_number)
            AcctTran.objects.create_acct_tran(user, ae, acct, amount*(-1))
            
    def get_acct_number(self, discount=False):
        if discount:
            return 466800
        else:
            return 406800
        
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
         
        # approve it
        if (self.status_detail).lower() <> 'active':
            self.status_detail = 'active'
        self.approved = 1
        self.approved_denied_dt = datetime.now()
        if not request.user.is_anonymous():
            self.approved_denied_user = request.user
        self.save()
        
        # send notification to administrators
        recipients = get_notice_recipients('module', 'corporatememberships', 'corporatemembershiprecipients')
        if recipients:
            if notification:
                extra_context = {
                    'object': self,
                    'request': request,
                }
                notification.send_emails(recipients,'corp_memb_paid', extra_context)
                
    def is_rep(self, this_user):
        """
        Check if this user is one of the representatives of this corporate membership.
        """
        if this_user.is_anonymous(): return False
        reps = self.reps.all()
        for rep in reps:
            if rep.id == this_user.id:
                return True
        return False
    
    def allow_view_by(self, this_user):
        if is_admin(this_user): return True
        
        if not this_user.is_anonymous():
            if self.is_rep(this_user): return True
            if self.creator:
                if this_user.id == self.creator.id: return True
            if self.owner:
                if this_user.id == self.owner.id: return True
                
        return False
    
    def allow_edit_by(self, this_user):
        if is_admin(this_user): return True
        
        if not this_user.is_anonymous():
            if self.status == 1 and self.status_detail == 'active':
                if self.is_rep(this_user): return True
                if self.creator:
                    if this_user.id == self.creator.id: return True
                if self.owner:
                    if this_user.id == self.owner.id: return True
                
        return False
    
    
    def get_renewal_period_dt(self):
        """
        calculate and return a tuple of renewal period dt:
         (renewal_period_start_dt, renewal_period_end_dt)
        """
        if not self.expiration_dt or not isinstance(self.expiration_dt, datetime):
            return (None, None)
        
        start_dt = self.expiration_dt - timedelta(days=self.corporate_membership_type.membership_type.renewal_period_start)
        end_dt = self.expiration_dt + timedelta(days=self.corporate_membership_type.membership_type.renewal_period_end)
        
        return (start_dt, end_dt)
        
    def can_renew(self):
        if not self.expiration_dt or not isinstance(self.expiration_dt, datetime):
            return False
        
        (renewal_period_start_dt, renewal_period_end_dt) = self.get_renewal_period_dt()
        
        now = datetime.now()
        return (now >= renewal_period_start_dt and now <= renewal_period_end_dt)
    
    @property
    def is_expired(self):
        if not self.expiration_dt or not isinstance(self.expiration_dt, datetime):
            return False
        return datetime.now() >= self.expiration_dt
    
    @property
    def is_in_grace_period(self):
        if self.is_expired:
            grace_period_end_dt = self.expiration_dt + timedelta(days=self.corporate_membership_type.membership_type.expiration_grace_period)
            return datetime.now() < grace_period_end_dt
        return False
    
    def archive(self, user=None):
        """
        Copy self to the CorporateMembershipArchive table
        """
        corp_memb_archive = CorporateMembershipArchive()
        
        field_names = [field.name for field in self.__class__._meta.fields]
        field_names.remove('id')
        
        for name in field_names:
            exec("corp_memb_archive.%s=self.%s" % (name, name))
            
        corp_memb_archive.corporate_membership = self
        corp_memb_archive.corp_memb_create_dt = self.create_dt
        corp_memb_archive.corp_memb_update_dt = self.update_dt
        corp_memb_archive.archive_user = user
        corp_memb_archive.save()
        
        
class AuthorizedDomain(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership", related_name="auth_domains")
    name = models.CharField(max_length=100)
        
class CorporateMembershipRep(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership",
                                             related_name="reps")
    user = models.ForeignKey(User, verbose_name=_("Representative"),)
    is_dues_rep = models.BooleanField(_('is dues rep?'), default=0, blank=True)
    is_member_rep = models.BooleanField(_('is member rep?'), default=0, blank=True)
    #is_alternate_rep = models.BooleanField(_('is alternate rep?'), default=0, blank=True)
    
    class Meta:
        unique_together = (("corporate_membership", "user"),)
    
    
class CorporateMembershipArchive(TendenciBaseModel):
    corporate_membership = models.ForeignKey('CorporateMembership')
    guid = models.CharField(max_length=50)
    corporate_membership_type = models.ForeignKey("CorporateMembershipType") 
    name = models.CharField(max_length=250)
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, default='', blank=True, null=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zip = models.CharField(_('zipcode'), max_length=50, blank=True, null=True)
    country = models.CharField(_('country'), max_length=50, blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=50, blank=True)
    email = models.CharField(_('email'), max_length=200,  blank=True)
    url = models.CharField(_('url'), max_length=100, blank=True, null=True)
    #authorized_domains = models.CharField(max_length=500, blank=True, null=True)
    secret_code = models.CharField(max_length=50, blank=True, null=True)
    
    renewal = models.BooleanField(default=0)
    renew_entry_id = models.IntegerField(default=0, blank=True, null=True) 
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField(_("Join Date Time")) 
    renew_dt = models.DateTimeField(_("Renew Date Time"), null=True) 
    expiration_dt = models.DateTimeField(_("Expiration Date Time"), null=True)
    approved = models.BooleanField(_("Approved"), default=0)
    approved_denied_dt = models.DateTimeField(_("Approved or Denied Date Time"), null=True)
    approved_denied_user = models.ForeignKey(User, null=True)
    payment_method = models.CharField(_("Payment Method"), max_length=50)

    corp_memb_create_dt = models.DateTimeField()
    corp_memb_update_dt = models.DateTimeField()
    
    archive_user = models.ForeignKey(User, related_name="corp_memb_archiver", null=True)
    
    
    class Meta:
        verbose_name = _("Corporate Membership Archive")
        verbose_name_plural = _("Corporate Membership Archives")
    
    def __unicode__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.member_number)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
        
class CorpMembRenewEntry(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership")
    corporate_membership_type = models.ForeignKey("CorporateMembershipType")
    payment_method = models.CharField(_("Payment Method"), max_length=50)
    
    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    
    create_dt = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True)
    status_detail = models.CharField(max_length=50)   # pending, approved and disapproved
    
class IndivMembRenewEntry(models.Model):
    corp_memb_renew_entry = models.ForeignKey("CorpMembRenewEntry")
    membership = models.ForeignKey(Membership)
    
    
class CorpFieldEntry(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership", related_name="fields")
    field = models.ForeignKey("CorpField", related_name="field")
    value = models.CharField(max_length=FIELD_MAX_LENGTH)
    
    
class CorpApp(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(_("URL Path"), max_length=155, unique=True)
    corp_memb_type = models.ManyToManyField("CorporateMembershipType", verbose_name=_("Corp. Memb. Type"))
    authentication_method = models.CharField(_("Authentication Method"), choices=AUTH_METHOD_CHOICES, 
                                    default='admin', max_length=50, 
                                    help_text='Define a method for individuals to be bound to their corporate memberships when signing up.')
    #description = models.TextField(_("Description"),blank=True, null=True, 
    #                               help_text='Will display at the top of the application form.')
    description = tinymce_models.HTMLField(_("Description"),blank=True, null=True, 
                                   help_text='Will display at the top of the application form.')
    notes = models.TextField(_("Notes"),blank=True, null=True, 
                                   help_text='Notes for editor. Will not display on the application form.')
    confirmation_text = models.TextField(_("Confirmation Text"), blank=True, null=True)
    
    memb_app = models.OneToOneField(App, help_text=_("App for individual memberships."), 
                                    related_name='corp_app', verbose_name=_("Membership Application")) 
   
    #use_captcha = models.BooleanField(_("Use Captcha"), default=1)
    #require_login = models.BooleanField(_("Require User Login"), default=0)
    
    class Meta:
        permissions = (("view_corpapp","Can view corporate membership application"),)
        verbose_name = _("Corporate Membership Application")
        verbose_name_plural = _("Corporate Membership Applications")
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ("corp_memb.add", [self.slug])
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
 
       
class CorpField(models.Model):
    corp_app = models.ForeignKey("CorpApp", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    # hidden fields - field_name and object_type
    field_name = models.CharField(_("Field Name"), max_length=30, blank=True, null=True, editable=False)
    #object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_type = models.CharField(_("Map to"), max_length=50, blank=True, null=True)
    field_type = models.CharField(_("Field Type"), choices=FIELD_CHOICES, max_length=80, 
                                  blank=True, null=True, default='CharField')
    
    order = models.IntegerField(_("Order"), default=0)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
                                help_text="Comma separated options where applicable")
    # checkbox/radiobutton
    field_layout = models.CharField(_("Choice Field Layout"), choices=FIELD_LAYOUT_CHOICES, 
                                    max_length=50, blank=True, null=True, default='1')
    size = models.CharField(_("Field Size"), choices=SIZE_CHOICES,  max_length=1,
                            blank=True, null=True, default='m')
                                  
    required = models.BooleanField(_("Required"), default=False)
    no_duplicates = models.BooleanField(_("No Duplicates"), default=False)
    visible = models.BooleanField(_("Visible"), default=True)
    admin_only = models.BooleanField(_("Admin Only"), default=0)   
    
    instruction = models.CharField(_("Instruction for User"), max_length=2000, blank=True, null=True)
    default_value = models.CharField(_("Predefined Value"), max_length=100, blank=True, null=True)
    css_class = models.CharField(_("CSS Class Name"), max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        ordering = ('order',)
        
    def __unicode__(self):
        if self.field_name:
            return '%s (field name: %s)' % (self.label, self.field_name)
        return '%s' % self.label
    
    def get_field_class(self, initial=None):
        """
            Generate the form field class for this field.
        """
        if self.label and self.id:
            if self.field_type not in ['section_break', 'page_break']:
                if self.field_name in ['corporate_membership_type', 'payment_method']:
                    if not self.field_type:
                        self.field_type = "ChoiceField/django.forms.RadioSelect"
                if "/" in self.field_type:
                    field_class, field_widget = self.field_type.split("/")
                else:
                    field_class, field_widget = self.field_type, None
                field_class = getattr(forms, field_class)
                field_args = {"label": self.label, 
                              "required": self.required,
                              'help_text':self.instruction}
                arg_names = field_class.__init__.im_func.func_code.co_varnames
                if initial:
                    field_args['initial'] = initial
                else:
                    if self.default_value:
                        field_args['initial'] = self.default_value
                if "max_length" in arg_names:
                    field_args["max_length"] = FIELD_MAX_LENGTH
                if "choices" in arg_names:
                    if self.field_name not in ['corporate_membership_type', 'payment_method']:
                        choices = self.choices.split(",")
                        field_args["choices"] = zip(choices, choices)
                if field_widget is not None:
                    module, widget = field_widget.rsplit(".", 1)
                    field_args["widget"] = getattr(import_module(module), widget)
                    
                return field_class(**field_args)
        return None
    
    def get_value(self, corporate_membership, **kwargs):
        if self.field_type not in ['section_break', 'page_break']:
            if self.field_name and self.object_type:
                if self.field_name == 'authorized_domains':
                    return ', '.join([ad.name for ad in corporate_membership.auth_domains.all()])
                if self.field_name == 'expiration_dt' and (not corporate_membership.expiration_dt):
                    return "Never Expire"
                if self.field_name == 'reps':
                    # get representatives
                    return CorporateMembershipRep.objects.filter(corporate_membership=corporate_membership).order_by('user')
                return eval("%s.%s" % (self.object_type, self.field_name))
            else:
                entry = self.field.filter(corporate_membership=corporate_membership)
                
                if entry:
                    return entry[0].value
        return ''
    
    def get_entry(self, corporate_membership, **kwargs):
        if self.field_type not in ['section_break', 'page_break']:
            if not (self.field_name and self.object_type):
                entry = self.field.filter(corporate_membership=corporate_membership)
                
                if entry:
                    return entry[0]
        return None
