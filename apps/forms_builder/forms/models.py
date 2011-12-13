
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User

from forms_builder.forms.settings import FIELD_MAX_LENGTH, LABEL_MAX_LENGTH
from forms_builder.forms.managers import FormManager
from perms.utils import is_admin
from perms.models import TendenciBaseModel
from user_groups.models import Group, GroupMembership

#STATUS_DRAFT = 1
#STATUS_PUBLISHED = 2
STATUS_CHOICES = (
    ('draft', "Draft"), 
    ('published', "Published"),
)

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
    ("CharField/forms_builder.forms.widgets.Description", _("Description")),
    ("CharField/forms_builder.forms.widgets.Header", _("Section Heading")),
    #("ModelMultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi checkbox")),
)

FIELD_FUNCTIONS = (
    ("GroupSubscription", _("Subscribe to Group")),
    ("EmailFirstName", _("First Name")),
    ("EmailLastName", _("Last Name")),
    ("EmailFullName", _("Full Name")),
    ("EmailPhoneNumber", _("Phone Number")),
)

class Form(TendenciBaseModel):
    """
    A user-built form.
    """

    title = models.CharField(_("Title"), max_length=50)
    slug = models.SlugField(editable=False, max_length=100, unique=True)
    intro = models.TextField(_("Intro"), max_length=2000)
    response = models.TextField(_("Confirmation Text"), max_length=2000)
    email_text = models.TextField(_("Email Text to Submitter"), default='', blank=True, help_text=
        _("If Send email is checked, this is the text that will be sent in an email to the person submitting the form."), max_length=2000)
#    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, 
#        default=STATUS_PUBLISHED)
    subject_template = models.CharField(_("Template for email subject "),  
        help_text=_("""Options include [title] for form title, and  
                        name of form fields inside brackets [ ]. E.x. [first name] or 
                        [email address]"""), 
        default="[title] - [first name]  [last name] - [phone]",
        max_length=200,
        blank=True, null=True)
    send_email = models.BooleanField(_("Send email"), default=False, help_text=
        _("If checked, the person entering the form will be sent an email"))
    email_from = models.EmailField(_("From address"), blank=True, 
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send copies to"), blank=True, 
        help_text=_("One or more email addresses, separated by commas"), 
        max_length=200)
    completion_url = models.URLField(_("Completion URL"), blank=True, null=True,
        help_text=_("Redirect to this page after form completion."))
    
    objects = FormManager()

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")
        permissions = (("view_form","Can view form"),)
    
    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Create a unique slug from title - append an index and increment if it 
        already exists.
        """
        if not self.slug:
            self.slug = slugify(self.title)
            i = 0
            while True:
                if i > 0:
                    if i > 1:
                        self.slug = self.slug.rsplit("-", 1)[0]
                    self.slug = "%s-%s" % (self.slug, i)
                if not Form.objects.filter(slug=self.slug):
                    break
                i += 1
        super(Form, self).save(*args, **kwargs)
        
    @models.permalink
    def get_absolute_url(self):
        return ("form_detail", (), {"slug": self.slug})

    def admin_link_view(self):
        url = self.get_absolute_url()
        return "<a href='%s'>%s</a>" % (url, ugettext("View on site"))
    admin_link_view.allow_tags = True
    admin_link_view.short_description = ""

    def admin_link_export(self):
        url = reverse("admin:form_export", args=(self.id,))
        return "<a href='%s'>%s</a>" % (url, ugettext("Export entries"))
    admin_link_export.allow_tags = True
    admin_link_export.short_description = ""

class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)

class Field(models.Model):
    """
    A field for a user-built form.
    'field_function' has the following options:
    "GroupSubscription" 
    - Subscribes form entries to the group specified
    - Required to be a BooleanField
    "EmailFirstName", "EmailLastName", "EmailPhoneNumber", "EmailFullName"
    - Markers for specific fields that need to be referenced in emails
    - Required to be a CharField
    - Includes their respective values to the email's subject
    """
    
    form = models.ForeignKey("Form", related_name="fields")
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES,
        max_length=64)
    field_function = models.CharField(_("Special Functionality"),
        choices=FIELD_FUNCTIONS, max_length=64, null=True, blank=True)
    function_params = models.CharField(_("Group Name or Names"),
        max_length=100, null=True, blank=True, help_text="Comma separated if more than one")
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True, 
        help_text="Comma separated options where applicable")
    position = models.PositiveIntegerField(_('position'), default=0)
    default = models.CharField(_("Default"), max_length=1000, blank=True,
        help_text="Default value of the field")
        
    objects = FieldManager()

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        order_with_respect_to = "form"
    
    def __unicode__(self):
        return self.label

    def execute_function(self, entry, value, user=None):
        if self.field_function == "GroupSubscription":
            if value:
                for val in self.function_params.split(','):
                    group = Group.objects.get(name=val)
                    if user:
                        try:
                            group_membership = GroupMembership.objects.get(group=group, member=user)
                        except GroupMembership.DoesNotExist:
                            group_membership = GroupMembership(group=group, member=user)
                            group_membership.creator_id = user.id
                            group_membership.creator_username = user.username
                            group_membership.role='subscriber'
                            group_membership.owner_id =  user.id
                            group_membership.owner_username = user.username
                            group_membership.save()
                    else:
                        entry.subscribe(group)  # subscribe form-entry to a group

class FormEntry(models.Model):
    """
    An entry submitted via a user-built form.
    """

    form = models.ForeignKey("Form", related_name="entries")
    entry_time = models.DateTimeField(_("Date/time"))
    entry_path = models.CharField(max_length=200, blank=True, default="")
    
    class Meta:
        verbose_name = _("Form entry")
        verbose_name_plural = _("Form entries")
        
    def __unicode__(self):
        u = ''
        for f in self.fields.all()[0:5]:
            u = u + str(f) + ' '
        return u[0:len(u)-1]

    @models.permalink
    def get_absolute_url(self):
        return ("form_entry_detail", (), {"id": self.pk})
    
    def subscribe(self, group):
        """
        Subscribe FormEntry to group specified.
        """
        # avoiding circular imports
        from subscribers.models import GroupSubscription as GS
        try:
            GS.objects.get(group=group, subscriber=self)
        except GS.DoesNotExist:
            GS.objects.create(group=group, subscriber=self)

    def unsubscribe(self, group):
        """
        Unsubscribe FormEntry from group specified
        """
        # avoiding circular imports
        from subscribers.models import GroupSubscription as GS
        try:
            sub = GS.objects.get(group=group, subscriber=self)
            sub.delete()
        except GS.DoesNotExist:
            pass
        
    def get_name_email(self):
        """Try to figure out the name and email from this entry
            Assume: 1) email field type is EmailField
                    2) use the labels to identify the name.
            We might need a better solution because this will not work 
            if the form is not in English, or labels for names are not 
            'first name', 'last name' or 'name'.
            Update: You can now use the special functions that start with
            "Email" to mark fields you need for this method 
            instead of relying on the label as a marker.
        """
        field_entries = self.fields.all()
        first_name = ""
        last_name = ""
        name = ""
        email = ""
        for entry in field_entries:
            field = entry.field
            if field.field_type.lower() == 'emailfield':
                email = entry.value
            if field.label.lower() in ['name']:
                name = entry.value
            if field.label.lower() in ['first name']:
                first_name = entry.value
            if field.label.lower() in ['last name']:
                last_name = entry.value
        if not name:
            if first_name or last_name:
                name = '%s %s' % (first_name, last_name)
        if not name:
            # pick the name from email
            if email:
                if  '@' in email:
                    name, domain = email.split('@')
                else:
                    name = email
            
        return (name, email)
        
    def get_value_of(self, field_function):
        """
        Returns the value of the a field entry based 
        on the field_function specified
        """
        for entry in self.fields.all():
            if entry.field.field_function == field_function:
                return entry.value
        return ''
    
    def get_type_of(self, field_type):
        """
        Returns the value of the a field entry based 
        on the field_type specified
        """
        for entry in self.fields.all():
            if entry.field.field_type.lower() == field_type:
                return entry.value
        return ''
        
    def get_first_name(self):
        return self.get_value_of("EmailFirstName")
        
    def get_last_name(self):
        return self.get_value_of("EmailLastName")
        
    def get_full_name(self):
        return self.get_value_of("EmailFullName")
        
    def get_phone_number(self):
        return self.get_value_of("EmailPhoneNumber")
        
    def get_email_address(self):
        return self.get_type_of("emailfield")
    
class FieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a user-built form.
    """
    
    entry = models.ForeignKey("FormEntry", related_name="fields")
    field = models.ForeignKey("Field", related_name="field")
    value = models.CharField(max_length=FIELD_MAX_LENGTH)

    class Meta:
        verbose_name = _("Form field entry")
        verbose_name_plural = _("Form field entries")
    
    def __unicode__(self):
        return ('%s: %s' % (self.field.label, self.value))
    
    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FieldEntry, self).save(*args, **kwargs)
        self.field.execute_function(self.entry, self.value, user=user)
    
class Pricing(models.Model):
    """
    Pricing options for custom payment forms.
    """
    form = models.ForeignKey('Form')
    label = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
