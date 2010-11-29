import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from perms.models import TendenciBaseModel
from invoices.models import Invoice
from memberships.models import MembershipType

FIELD_CHOICES = (
                    ("CharField", _("Text")),
                    ("CharField/django.forms.Textarea", _("Paragraph Text")),
                    ("BooleanField", _("Checkbox")),
                    ("ChoiceField", _("Choose from a list")),
                    ("MultipleChoiceField", _("Multi select")),
                    ("EmailField", _("Email")),
                    ("FileField", _("File upload")),
                    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
                    ("DateTimeField", _("Date/time")),
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
    name = models.CharField(max_length=250)
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, default='', blank=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zip = models.CharField(_('zipcode'), max_length=50, blank=True)
    country = models.CharField(_('country'), max_length=50, blank=True)
    phone = models.CharField(_('phone'), max_length=50, blank=True)
    email = models.CharField(_('email'), max_length=200,  blank=True)
    url = models.CharField(_('url'), max_length=100, blank=True)
    authorized_domains = models.CharField(max_length=500)
    
    renewal = models.BooleanField(default=0)
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField(_("Join Date Time")) 
    renew_dt = models.DateTimeField(_("Renew Date Time")) 
    expiration_dt = models.DateTimeField(_("Expiration Date Time"))
    approved = models.BooleanField(_("Approved"), default=0)
    approved_denied_dt = models.DateTimeField(_("Approved or Denied Date Time"))
    approved_denied_user = models.ForeignKey(User, verbose_name=_("Approved or Denied User"))
    payment_method = models.CharField(_("Payment Method"), max_length=50)
    
    cma = models.ForeignKey("CorporateMembershipApp")
    
    class Meta:
        verbose_name = _("Corporate Membership")
        verbose_name_plural = _("Corporate Memberships")
    
    def __unicode__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.member_number)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
        
class CorporateMembershipDuesrep(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership", related_name="dues_rep")
    user = models.ForeignKey(User)
    
    
class CorporateMembershipArchive(models.Model):
    guid = models.CharField(max_length=50)
    corporate_membership_type = models.ForeignKey("CorporateMembershipType") 
    name = models.CharField(max_length=250)
    address = models.CharField(_('address'), max_length=150, blank=True)
    address2 = models.CharField(_('address2'), max_length=100, default='', blank=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zip = models.CharField(_('zipcode'), max_length=50, blank=True)
    country = models.CharField(_('country'), max_length=50, blank=True)
    phone = models.CharField(_('phone'), max_length=50, blank=True)
    email = models.CharField(_('email'), max_length=200,  blank=True)
    url = models.CharField(_('url'), max_length=100, blank=True)
    authorized_domains = models.CharField(max_length=500)
    
    renewal = models.BooleanField(default=0)
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField(_("Join Date Time")) 
    renew_dt = models.DateTimeField(_("Renew Date Time")) 
    expiration_dt = models.DateTimeField(_("Expiration Date Time"))
    approved = models.BooleanField(_("Approved"), default=0)
    approved_denied_dt = models.DateTimeField(_("Approved or Denied Date Time"))
    approved_denied_user = models.ForeignKey(User)
    payment_method = models.CharField(_("Payment Method"), max_length=50)
    
    create_dt = models.DateTimeField()
    update_dt = models.DateTimeField()
    creator_id = models.IntegerField(default=0)
    creator_username = models.CharField(max_length=50)
    owner_id = models.IntegerField(default=0)   
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField()
    status_detail = models.CharField(max_length=50)
    
    archive_dt = models.DateTimeField()
    archive_user = models.ForeignKey(User, related_name="corp_memb_archiver")
    
    
    class Meta:
        verbose_name = _("Corporate Membership")
        verbose_name_plural = _("Corporate Memberships")
    
    def __unicode__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.member_number)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
    
class CorporateMembershipCustomFieldEntry(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership")
    cma_field = models.ForeignKey("CorporateMembershipAppField", related_name="entries")
    value = models.CharField(max_length=500)
    
    
class CorporateMembershipApp(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_("Application Name"), max_length=155)
    slug = models.SlugField(editable=False, max_length=155, unique=True)
    notes = models.CharField(_("Notes"), max_length=255)
   
    use_captcha = models.BooleanField(_("Use Captcha"), default=1)
    require_login = models.BooleanField(_("Require User Login"), default=0)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
        
class CorporateMembershipAppPage(models.Model):
    cma = models.ForeignKey("CorporateMembershipApp", related_name="pages")
    order = models.IntegerField(_("Order"), default=0)
 
class CorporateMembershipAppSection(models.Model):
    cma = models.ForeignKey("CorporateMembershipApp", related_name="sections")
    cma_page = models.ForeignKey("CorporateMembershipAppPage", related_name="sections")
    
    label = models.CharField(_("Label"), max_length=120)
    description = models.CharField(_("Description"), max_length=500)
    admin_only = models.BooleanField(_("Admin Only"), default=0)
    
    order = models.IntegerField(_("Order"), default=0)
    css_class = models.CharField(_("CSS Class Name"), max_length=50)
    
       
class CorporateMembershipAppField(models.Model):
    cma = models.ForeignKey("CorporateMembershipApp", related_name="fields")
    cma_section = models.ForeignKey("CorporateMembershipAppSection", related_name="fields")
    
    #object_type = models.CharField(_("Object Type"), max_length=50)
    object_type = models.ForeignKey(ContentType, blank=True, null=True)
    label = models.CharField(_("Label"), max_length=200)
    field_name = models.CharField(_("Field Name"), max_length=50)
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES, max_length=50, 
                                  blank=True, null=True)
    size = models.IntegerField(_("Field Size"), default=0)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
                                help_text="Comma separated options where applicable")
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    admin_only = models.BooleanField(_("Admin Only"), default=0)
    editor_only = models.BooleanField(_("Editor Only"), default=0) 
    
    order = models.IntegerField(_("Order"), default=0)
    css_class = models.CharField(_("CSS Class Name"), max_length=50)


    