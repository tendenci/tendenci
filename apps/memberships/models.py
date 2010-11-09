import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from perms.models import TendenciBaseModel
from invoices.models import Invoice
from directories.models import Directory
from user_groups.models import Group
from corporate_memberships.models import CorporateMembership

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
OBJECT_TYPE_CHOICES = (
                        ("user", _("User")),
                        ("membership", _("Membership")),
                        ("directory", _("Directory")),
                        ("donation", _("Donation")),
                        ("custom", _("Custom")),
                       )
PERIOD_CHOICES = (
                  ("fixed", _("Fixed")),
                  ("rolling", _("Rolling")),
                  )
PERIOD_UNIT_CHOICES = (
                       ("days", _("Days")),
                       ("months", _("Months")),
                       ("years", _("Years")),
                       )

class MembershipType(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.CharField(_('Description'), max_length=500)
    price = models.DecimalField(_('Price'), max_digits=15, decimal_places=2, blank=True, default=0,
                                help_text="Set 0 for free membership.")
    # for first time processing
    admin_fee = models.DecimalField(_('Admin Fee'), 
                                    max_digits=15, decimal_places=2, blank=True, default=0, 
                                    help_text="Admin fee for the first time processing")
    
    group = models.ForeignKey(Group, related_name="membership_types",
                              help_text="Members joined will be added to this group")
    
    require_approval = models.BooleanField(_('Require Approval'), default=1)
    renewal = models.BooleanField(_('Renewal Only'), default=0)
    order = models.IntegerField(_('Order'), default=0, 
                                help_text='Types will be displayed in ascending order based on this field')
    admin_only = models.BooleanField(_('Admin Only'), default=0)  # from allowuseroption
    
    #expiration_method = models.CharField(_('Expiration Method'), max_length=50)
    #expiration_method_custom_dt = models.DateTimeField()
    period = models.IntegerField(_('Period'), default=0)
    period_unit = models.CharField(choices=PERIOD_UNIT_CHOICES, max_length=10)
    period_type = models.CharField(_("Period Type"),default='rolling', choices=PERIOD_CHOICES, max_length=10)
    
    expiration_method = models.CharField(_('Expires On'), max_length=50)
    expiration_method_day = models.IntegerField(_('Expiration Day'), default=0)
    renew_expiration_method = models.CharField(_('Renewal Expires On'), max_length=50)
    renew_expiration_day = models.IntegerField(default=0)
    renew_expiration_day2 = models.IntegerField(default=0)
    
    fixed_expiration_method = models.CharField(_('Expires On'), max_length=50)
    fixed_expiration_day = models.IntegerField(default=0)
    fixed_expiration_month = models.IntegerField(default=0)
    fixed_expiration_year = models.IntegerField(default=0)
    fixed_expiration_day2 = models.IntegerField(default=0)
    fixed_expiration_month2 = models.IntegerField(default=0)
    
    fixed_expiration_rollover = models.BooleanField(_("Allow Rollover"), default=0)
    fixed_expiration_rollover_days = models.IntegerField(default=0, 
            help_text=_("Membership signups after this date covers the following calendar year as well."))
    
    renewal_period_start = models.IntegerField(_('Renewal Period Start'), default=0, 
            help_text="How long (in days) before the memberships expires can the member renew their membership.")
    renewal_period_end = models.IntegerField(_('Renewal Period End'), default=0, 
            help_text="How long (in days) after the memberships expires can the member renew their membership.")
    expiration_grace_period = models.IntegerField(_('Expiration Grace Period'), default=0, 
            help_text="The number of days after the membership expires their membership is still active.")
   
    corporate_membership_only = models.BooleanField(_('Corporate Membership Only'), default=0)
    corporate_membership_type_id = models.IntegerField(_('Corporate Membership Type'), default=0,
            help_text='If corporate membership only is checked, select a corporate membership type to associate with.')
    
    #ma = models.ManyToManyField("MembershipApplication", blank=True, null=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
 
    
class Membership(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    member_number = models.CharField(_("Member Number"), max_length=50)
    membership_type = models.ForeignKey("MembershipType", verbose_name=_("Membership Type")) 
    user = models.ForeignKey(User, related_name="memberships")
    
    directory = models.ForeignKey(Directory, blank=True, null=True) 
    
    renewal = models.BooleanField(default=0)
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField(_("Join Date Time")) 
    renew_dt = models.DateTimeField(_("Renew Date Time")) 
    expiration_dt = models.DateTimeField(_("Expiration Date Time"))
    approved = models.BooleanField(_("Approved"), default=0)
    approved_denied_dt = models.DateTimeField(_("Approved or Denied Date Time"))
    approved_denied_user = models.ForeignKey(User, verbose_name=_("Approved or Denied User"))
    # maybe change to foreign key to corporate_membership
    corporate_membership = models.ForeignKey(CorporateMembership, related_name="memberships")
    payment_method = models.CharField(_("Payment Method"), max_length=50)
    
    # add membership application id - so we can support multiple applications
    ma = models.ForeignKey("MembershipApplication")
    
    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
    
    def __unicode__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.member_number)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
    
class MembershipArchive(models.Model):
    guid = models.CharField(max_length=50)
    member_number = models.CharField(max_length=50)
    membership_type = models.ForeignKey("MembershipType")
    user = models.ForeignKey(User, related_name="membership_archives")
    
    directory = models.ForeignKey(Directory, blank=True, null=True) 
    
    renewal = models.BooleanField(default=0)
    invoice = models.ForeignKey(Invoice, blank=True, null=True) 
    join_dt = models.DateTimeField() 
    renew_dt = models.DateTimeField() 
    expiration_dt = models.DateTimeField()
    approved = models.BooleanField(default=0)
    approved_denied_dt = models.DateTimeField()
    approved_denied_user_id =  models.IntegerField(default=0)
    # maybe change to foreign key to corporate_membership
    corporate_membership_id = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=50)
    
    ma_id = models.IntegerField()
    
    # these fields should be copied from Membership table
    create_dt = models.DateTimeField()
    update_dt = models.DateTimeField()
    #creator = models.ForeignKey(User, editable=False, related_name="memb_archives_creator")
    creator_id = models.IntegerField(default=0)
    creator_username = models.CharField(max_length=50)
    owner_id = models.IntegerField(default=0)   
    owner_username = models.CharField(max_length=50)
    status = models.BooleanField()
    status_detail = models.CharField(max_length=50)
    
    # the actual archive datetime and user
    archive_dt = models.DateTimeField()
    archive_user = models.ForeignKey(User, related_name="membership_archiver")
    
    def __unicode__(self):
        return "%s (%s)" % (self.user.get_full_name(), self.member_number) 
    
class MembershipCustomFieldEntry(models.Model):
    membership = models.ForeignKey("Membership", related_name="entries")
    ma_field = models.ForeignKey("MembershipApplicationField", related_name="entries")
    value = models.CharField(max_length=500)
    
    
class MembershipApplication(TendenciBaseModel):
    guid = models.CharField(max_length=50)
    name = models.CharField(_("Application Name"), max_length=155)
    slug = models.SlugField(max_length=155, unique=True)
    notes = models.CharField(_("Notes"), max_length=255)
   
    use_captcha = models.BooleanField(_("Use Captcha"), default=1)
    require_login = models.BooleanField(_("Require User Login"), default=0)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)
        
class MembershipApplicationPage(models.Model):
    ma = models.ForeignKey("MembershipApplication", related_name="pages")
    sort_order = models.IntegerField(_("Sort Order"), default=0)
 
class MembershipApplicationSection(models.Model):
    ma = models.ForeignKey("MembershipApplication", related_name="sections")
    ma_page = models.ForeignKey("MembershipApplicationPage", related_name="sections")
    
    label = models.CharField(_("Label"), max_length=120)
    description = models.CharField(_("Description"), max_length=500)
    admin_only = models.BooleanField(_("Admin Only"), default=0)
    
    order = models.IntegerField(_("Order"), default=0)
    css_class = models.CharField(_("CSS Class Name"), max_length=50)
    
       
class MembershipApplicationField(models.Model):
    ma = models.ForeignKey("MembershipApplication", related_name="fields")
    ma_section = models.ForeignKey("MembershipApplicationSection", related_name="fields")
    
    #object_type = models.CharField(_("Object Type"), choices=OBJECT_TYPE_CHOICES, max_length=50)
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


    