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

FIELD_LAYOUT_CHOICES = (
                        ('1', _('One Column')),
                        ('2', _('Two Columns')),
                        ('3', _('Three Columns')),
                        ('0', _('Side by Side')),
                        )
AUTH_METHOD_CHOICES = (
                       ('email', _('E-mail')),
                       ('admin', _('Admin')),
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
    
    cma = models.ForeignKey("CorpApp")
    
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
    
class CorpFieldEntry(models.Model):
    corporate_membership = models.ForeignKey("CorporateMembership")
    cma_field = models.ForeignKey("CorpAppField", related_name="entries")
    value = models.CharField(max_length=500)
    
    
class CorpApp(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(max_length=155, unique=True)
    corp_memb_type = models.ManyToManyField("CorporateMembershipType", verbose_name=_("Corp. Memb. Type"))
    authentication_method = models.CharField(_("Authentication Method"), choices=AUTH_METHOD_CHOICES, 
                                    default='admin', max_length=50, 
                                    help_text='for individuals applying under a Corporate Membership')
    notes = models.CharField(_("Notes"), max_length=255)
   
    use_captcha = models.BooleanField(_("Use Captcha"), default=1)
    require_login = models.BooleanField(_("Require User Login"), default=0)
    
    class Meta:
        verbose_name = _("Corporate Membership Application")
        verbose_name_plural = _("Corporate Membership Applications")
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
        
class CorpAppPage(models.Model):
    #cma = models.ForeignKey("CorpApp", related_name="pages")
    title = models.CharField(_("Title"), max_length=120, blank=True, null=True)
    top_instruction = models.CharField(_("Top Instruction"), max_length=500, blank=True, null=True)
    bottom_instruction = models.CharField(_("Bottom Instruction"), max_length=500, blank=True, null=True)
    order = models.IntegerField(_("Page #"), default=0)
    css_class = models.CharField(_("CSS Class Name"), max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ('order',)
        
    def __unicode__(self):
        return 'Page #%d: %s' % (self.order, self.title)
 
class CorpAppSection(models.Model):
    #cma = models.ForeignKey("CorpApp",  related_name="sections")
    #cma_page = models.ForeignKey("CorpAppPage", verbose_name=_("Page"),  
    #                             related_name="sections",
    #                             blank=True, null=True)
    
    label = models.CharField(_("Section Label"), max_length=120)
    description = models.CharField(_("Description"), max_length=500, blank=True, null=True)
    admin_only = models.BooleanField(_("Admin Only"), default=0)
    
    #order = models.IntegerField(_("Order"), default=0)
    css_class = models.CharField(_("CSS Class Name"), max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")
        #ordering = ('order',)
        
    def __unicode__(self):
        return '%s' % (self.label)
    
       
class CorpAppField(models.Model):
    #cma = models.ForeignKey("CorpApp", related_name="fields")
    #cma_section = models.ForeignKey("CorpAppSection", verbose_name=_("Section"), 
    #                                related_name="fields",
    #                                blank=True, null=True)
    
    #object_type = models.ForeignKey(ContentType, blank=True, null=True)
    label = models.CharField(_("Label"), max_length=200)
    field_name = models.CharField(_("Field Name"), max_length=30)
    field_type = models.CharField(_("Field Type"), choices=FIELD_CHOICES, max_length=50, 
                                  blank=True, null=True)
    
    #order = models.IntegerField(_("Order"), default=0)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
                                help_text="Comma separated options where applicable")
    # checkbox/radiobutton
    field_layout = models.CharField(_("Choice Field Layout"), choices=FIELD_LAYOUT_CHOICES, 
                                    max_length=50, blank=True, null=True)
    size = models.CharField(_("Field Size"), choices=SIZE_CHOICES,  max_length=1,
                            blank=True, null=True)
                                  
    required = models.BooleanField(_("Required"), default=True)
    no_duplicates = models.BooleanField(_("No Duplicates"), default=False)
    visible = models.BooleanField(_("Visible"), default=True)
    admin_only = models.BooleanField(_("Admin Only"), default=0)
    #editor_only = models.BooleanField(_("Editor Only"), default=0) 
    
    
    help_text = models.CharField(_("Instruction for User"), max_length=100, blank=True, null=True)
    default_value = models.CharField(_("Predefined Value"), max_length=50, blank=True, null=True)
    css_class = models.CharField(_("CSS Class Name"), max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        #ordering = ('order',)
        
    def __unicode__(self):
        return '%s' % self.label
    
    
class CorpField(models.Model):
    cma = models.ForeignKey("CorpApp", related_name="cma_fields")
    page = models.ForeignKey("CorpAppPage", verbose_name=_("Page"),  
                                 related_name="page_fields",
                                 blank=True, null=True)
    section = models.ForeignKey("CorpAppSection", verbose_name=_("Section"), 
                                    related_name="section_fields",
                                    blank=True, null=True)
    field = models.ForeignKey("CorpAppField", verbose_name=_("Field"), 
                                    related_name="field_fields",
                                    blank=True, null=True)
    order = models.IntegerField(_("Order"), default=0)
    
    class Meta:
        verbose_name = _("Form Field")
        verbose_name_plural = _("Form Fields")
        ordering = ('order',)
        
    def __unicode__(self):
        return '%s' % self.field.label


    