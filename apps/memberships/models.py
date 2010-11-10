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

    ma = models.ForeignKey("App", blank=True, null=True)

    class Meta:
        verbose_name = "Membership Type"
    
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
    ma = models.ForeignKey("App")
    
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
    
    
class App(TendenciBaseModel):
    guid = models.CharField(max_length=50, editable=False)
    name = models.CharField(_("Name"), max_length=155)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True,
        help_text="Description of this application. Displays at top of application.")
    confirmation_text = models.TextField(_("Confirmation Text"), blank=True, 
        help_text="Text the submitter sees after submitting.")
    notes = models.TextField(blank=True,
        help_text="Extra notes about this application for editors.  Hidden actual application.")
    use_captcha = models.BooleanField(_("Use Captcha"), default=1)

    class Meta:
        verbose_name = "Membership Application"

    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid1())
        super(self.__class__, self).save(*args, **kwargs)

class AppField(models.Model):
    app = models.ForeignKey("App", related_name="fields")
    label = models.CharField(_("Label"), max_length=200)
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES, max_length=50)
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
        help_text="Comma separated options where applicable")
    position = models.IntegerField(blank=True)

    def save(self, *args, **kwargs):
        model = self.__class__
        
        if self.position is None:
            # Append
            try:
                last = model.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0
        
        return super(AppField, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        ordering = ('position',)

    def __unicode__(self):
        return self.label

class AppEntry(models.Model):
    """
    An entry submitted via a membership application.
    """
    
    app = models.ForeignKey("App", related_name="entries")
    entry_time = models.DateTimeField(_("Date/Time"))

    class Meta:
        verbose_name = _("Application Entry")
        verbose_name = _("Application Entries")

#    @models.permalink
#    def get_absolute_url(self):
#        return ("app.entry.detail", (), {"id": self.pk})

class AppFieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a membership application.
    """
    
    entry = models.ForeignKey("AppEntry", related_name="fields")
    field = models.ForeignKey("AppField", related_name="field")
    value = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = _("Application Field Entry")
        verbose_name = _("Application Field Entries")


