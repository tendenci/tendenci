from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.safestring import mark_safe

from django_countries import countries as COUNTRIES
from localflavor.us.us_states import STATE_CHOICES
from localflavor.ca.ca_provinces import PROVINCE_CHOICES

from tendenci.apps.forms_builder.forms.settings import FIELD_MAX_LENGTH, LABEL_MAX_LENGTH
from tendenci.apps.forms_builder.forms.managers import FormManager
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.user_groups.models import Group, GroupMembership
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.utils import checklist_update
from tendenci.libs.abstracts.models import OrderingBaseModel
from tendenci.apps.user_groups.utils import get_default_group

#STATUS_DRAFT = 1
#STATUS_PUBLISHED = 2
STATUS_CHOICES = (
    ('draft', _("Draft")),
    ('published', _("Published")),
)

FIELD_CHOICES = (
    ("CharField", _("Text")),
    ("CharField/django.forms.Textarea", _("Paragraph Text")),
    ("BooleanField", _("Checkbox")),
    ("ChoiceField/django.forms.RadioSelect", _("Single-select - Radio Button")),
    ("ChoiceField", _("Single-select - From a List")),
    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi-select - Checkboxes")),
    ("MultipleChoiceField", _("Multi-select - From a List")),
    ("EmailVerificationField", _("Email")),
    ("CountryField", _("Countries")),
    ("StateProvinceField", _("States/Provinces")),
    ("FileField", _("File upload")),
    ("DateField/django.forms.widgets.SelectDateWidget", _("Date - Select")),
    ("DateField/django.forms.DateInput", _("Date - Text Input")),
    ("DateTimeField", _("Date/time")),
    ("CharField/tendenci.apps.forms_builder.forms.widgets.Description", _("Description")),
    ("CharField/tendenci.apps.forms_builder.forms.widgets.Header", _("Section Heading")),
)

FIELD_FUNCTIONS = (
    ("GroupSubscription", _("Subscribe to Group")),
    ("GroupSubscriptionAuto", _("Subscribe to Group (Auto)")),
    ("EmailFirstName", _("First Name")),
    ("EmailLastName", _("Last Name")),
    ("EmailFullName", _("Full Name")),
    ("EmailPhoneNumber", _("Phone Number")),
    ("Recipients", _("Email to Recipients")),
    ("company", _("Company")),
    ("address", _("Address")),
    ("city", _("City")),
    ("region", _("Region")),
    ("state", _("State")),
    ("zipcode", _("Zip")),
    ("position_title", _("Position Title")),
    ("referral_source", _("Referral Source")),
    ("notes", _("Notes")),
)

BILLING_PERIOD_CHOICES = (
    ('month', _('Month(s)')),
    ('year', _('Year(s)')),
    ('week', _('Week(s)')),
    ('day', _('Day(s)')),
)

DUE_SORE_CHOICES = (
    ('start', _('start')),
    ('end', _('end')),
)


class Form(TendenciBaseModel):
    """
    A user-built form.
    """

    FIRST = 1
    MIDDLE = 2
    LAST = 3

    FIELD_POSITION_CHOICES = (
        (FIRST, _("First")),
        (MIDDLE, _("Middle")),
        (LAST, _("Last")),
    )

    INTRO_DEFAULT_NAME = _("Intro")
    FIELDS_DEFAULT_NAME = _("Fields")
    PRICING_DEFAULT_NAME = _("Pricings")

    title = models.CharField(_("Title"), max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    intro = models.TextField(_("Intro"), max_length=2000, blank=True)
    response = models.TextField(_("Confirmation Text"), max_length=2000, blank=True)
    email_text = models.TextField(_("Email Text to Submitter"), default='', blank=True,
        help_text=_("If Send email is checked, this is the text that will be sent in an email to the person submitting the form."), max_length=2000)
    subject_template = models.CharField(_("Template for email subject "),
        help_text=_("""Options include [title] for form title, and
                        name of form fields inside brackets [ ]. E.x. [first name] or
                        [email address]"""),
        default="[title] - [first name]  [last name] - [phone]",
        max_length=200,
        blank=True, null=True)
    send_email = models.BooleanField(_("Send email"), default=False,
        help_text=_("If checked, the person submitting the form will be sent an email."))
    email_from = models.EmailField(_("Reply-To address"), blank=True,
        help_text=_("The address the replies to the email will be sent to"))
    email_copies = models.CharField(_("Send copies to"), blank=True,
        help_text=_("One or more email addresses, separated by commas"),
        max_length=2000)
    completion_url = models.CharField(_("Completion URL"), max_length=1000, blank=True, null=True,
        help_text=_("Redirect to this page after form completion. Absolute URLS should begin with http. Relative URLs should begin with a forward slash (/)."))
    template = models.CharField(_('Template'), max_length=50, blank=True)
    group = models.ForeignKey(Group, null=True, default=None, on_delete=models.SET_NULL)

    # payments
    custom_payment = models.BooleanField(_("Is Custom Payment"), default=False,
        help_text=_("If checked, please add pricing options below. Leave the price blank if users can enter their own amount."))
    recurring_payment = models.BooleanField(_("Is Recurring Payment"), default=False,
        help_text=_("If checked, please add pricing options below. Leave the price blank if users can enter their own amount. Please also add an email field as a required field with type 'email'"))
    payment_methods = models.ManyToManyField("payments.PaymentMethod", blank=True)

    perms = GenericRelation(ObjectPermission,
        object_id_field="object_id", content_type_field="content_type")

    # positions for displaying the fields
    intro_position = models.IntegerField(_("Intro Position"), choices=FIELD_POSITION_CHOICES, default=FIRST)
    fields_position = models.IntegerField(_("Fields Position"), choices=FIELD_POSITION_CHOICES, default=MIDDLE)
    pricing_position = models.IntegerField(_("Pricing Position"), choices=FIELD_POSITION_CHOICES, default=LAST)

    # variable name of form main sections
    intro_name = models.CharField(_("Intro Name"), max_length=50,
                                  default=INTRO_DEFAULT_NAME, blank=True)
    fields_name = models.CharField(_("Fields Name"), max_length=50,
                                   default=FIELDS_DEFAULT_NAME, blank=True)
    pricing_name = models.CharField(_("Pricing Name"), max_length=50,
                                    default=PRICING_DEFAULT_NAME, blank=True)

    objects = FormManager()

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")
#         permissions = (("view_form", _("Can view form")),)
        app_label = 'forms'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If this is the current contact form, update checklist
        if str(self.pk) == get_setting('site', 'global', 'contact_form'):
            checklist_update('update-contact')
        if not self.group:
            self.group_id = get_default_group()
        super(Form, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('form_detail', kwargs={"slug": self.slug})

    def get_payment_type(self):
        if self.recurring_payment and self.custom_payment:
            return _("Custom Recurring Payment")
        if self.recurring_payment:
            return _("Recurring Payment")
        if self.custom_payment:
            return _("Custom Payment")

    @mark_safe
    def admin_link_view(self):
        url = self.get_absolute_url()
        return "<a href='%s'>%s</a>" % (url, ugettext("View on site"))
    admin_link_view.short_description = ""

    @mark_safe
    def admin_link_export(self):
        url = reverse("admin:forms_form_export", args=(self.id,))
        return "<a href='%s'>%s</a>" % (url, ugettext("Export entries"))
    admin_link_export.short_description = ""

    def has_files(self):
        for field in self.fields.all():
            if field.field_type == 'FileField':
                return True
        return False


class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)

    """
    Get all Auto-fields. (As of writing, this is only GroupSubscriptionAuto)
    """
    def auto_fields(self):
        return self.filter(visible=False, field_function="GroupSubscriptionAuto")


class Field(OrderingBaseModel):
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

    form = models.ForeignKey("Form", related_name="fields", on_delete=models.CASCADE)
    label = models.CharField(_("Label"), max_length=LABEL_MAX_LENGTH)
    field_type = models.CharField(_("Type"), choices=FIELD_CHOICES,
        max_length=64)
    field_function = models.CharField(_("Special Functionality"),
        choices=FIELD_FUNCTIONS, max_length=64, null=True, blank=True)
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=1000, blank=True,
        help_text=_("Comma separated options where applicable"))
    default = models.CharField(_("Default"), max_length=1000, blank=True,
        help_text=_("Default value of the field"))

    objects = FieldManager()

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        #order_with_respect_to = "form"
        app_label = 'forms'

    def __str__(self):
        return self.label

    def get_field_class(self):
        if "/" in self.field_type:
            field_class, field_widget = self.field_type.split("/")
        else:
            field_class = self.field_type
        return field_class

    def get_field_widget(self):
        if "/" in self.field_type:
            field_class, field_widget = self.field_type.split("/")
        else:
            field_widget = None
        return field_widget

    def get_choices(self):
        if self.field_type == 'CountryField':
            exclude_list = ['GB', 'US', 'CA']
            countries = ((name,name) for key,name in COUNTRIES if key not in exclude_list)
            initial_choices = ((_('United States'), _('United States')),
                               (_('Canada'), _('Canada')),
                               (_('United Kingdom'), _('United Kingdom')),
                               ('','-----------'))
            choices = initial_choices + tuple(countries)
        elif self.field_type == 'StateProvinceField':
            choices = (('','-----------'),) + tuple((state, state_f.title()) for state, state_f in STATE_CHOICES) \
                                + tuple((prov, prov_f.title()) for prov, prov_f in PROVINCE_CHOICES)
            choices = sorted(choices)
        elif self.field_function == 'Recipients':
            choices = [(label+':'+val, label) for label, val in (i.split(":") for i in self.choices.split(","))]
        else:
            choices = [(val, val) for val in self.choices.split(",")]
        return choices

    def execute_function(self, entry, value, user=None):
        if self.field_function in ["GroupSubscription", "GroupSubscriptionAuto"]:
            if value:
                for val in self.choices.split(','):
                    group, created = Group.objects.get_or_create(name=val.strip())
                    if user and group.allow_self_add:
                        try:
                            group_membership = GroupMembership.objects.get(group=group, member=user)
                        except GroupMembership.DoesNotExist:
                            group_membership = GroupMembership(group=group, member=user)
                            group_membership.creator_id = user.id
                            group_membership.creator_username = user.username
                            group_membership.role = 'subscriber'
                            group_membership.owner_id = user.id
                            group_membership.owner_username = user.username
                            group_membership.save()


class FormEntry(models.Model):
    """
    An entry submitted via a user-built form.
    """

    form = models.ForeignKey("Form", related_name="entries", on_delete=models.CASCADE)
    entry_time = models.DateTimeField(_("Date/time"))
    entry_path = models.CharField(max_length=200, blank=True, default="")
    payment_method = models.ForeignKey('payments.PaymentMethod', null=True, on_delete=models.SET_NULL)
    pricing = models.ForeignKey('Pricing', null=True, on_delete=models.SET_NULL)
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    creator = models.ForeignKey(User, related_name="formentry_creator",  null=True, on_delete=models.SET_NULL)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Form entry")
        verbose_name_plural = _("Form entries")
        app_label = 'forms'

    def __str__(self):
        return ('%s submission' % (self.form.title,))

    def get_absolute_url(self):
        return reverse('form_entry_detail', kwargs={"id": self.pk})

    @property
    def owner(self):
        return self.creator
    
    @property
    def group(self):
        return self.form.group

    def entry_fields(self):
        return self.fields.all().order_by('field__position')

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
            if field.field_type.lower() == 'emailverificationfield':
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
                if '@' in email:
                    name, domain = email.split('@')
                else:
                    name = email

        return (name, email)

    def get_value_of(self, field_function):
        """
        Returns the value of the a field entry based
        on the field_function specified
        """
        for entry in self.fields.order_by('field__position'):
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

    def get_company(self):
        return self.get_value_of("company")

    def get_address(self):
        return self.get_value_of("address")

    def get_city(self):
        return self.get_value_of("city")

    def get_region(self):
        return self.get_value_of("region")

    def get_state(self):
        return self.get_value_of("state")

    def get_zipcode(self):
        return self.get_value_of("zipcode")

    def get_position_title(self):
        return self.get_value_of("position_title")
 
    def get_referral_source(self):
        return self.get_value_of("referral_source")

    def get_notes(self):
        return self.get_value_of("notes")

    def get_function_email_recipients(self):
        email_list = set()
        for entry in self.fields.order_by('field__position'):
            if entry.field.field_function == 'Recipients' and entry.value:
                if entry.field.field_type == 'BooleanField':
                    for email in entry.field.choices.split(","):
                        email_list.add(email.strip())
                else:
                    for email in entry.value.split(","):
                        email = email.split(":")
                        if len(email) > 1:
                            email_list.add(email[1].strip())
        return email_list

    def get_email_address(self):
        return self.get_type_of("emailverificationfield")

    # Called by payments_pop_by_invoice_user in Payment model.
    def get_payment_description(self, inv):
        """
        The description will be sent to payment gateway and displayed on invoice.
        If not supplied, the default description will be generated.
        This will pass the First Name and Last Name from the "Billing Information" screen, the value in the "Site Display Name"
        setting in Site Settings, and the name of the form that was submitted.
        """
        description = '%s Invoice %d, form: "%s", Form Entry Id (%d), billed to: %s %s.' % (
            get_setting('site', 'global', 'sitedisplayname'),
            inv.id,
            self.form.title,
            inv.object_id,
            inv.bill_to_first_name,
            inv.bill_to_last_name,
        )

        return description

    def set_group_subscribers(self):
        for entry in self.fields.filter(field__field_function__in=["GroupSubscription", "GroupSubscriptionAuto"]):
            entry.field.execute_function(self, entry.value, user=self.creator)

    def check_and_create_user(self):
        """
        Check and create a new user if needed (only if payment is involved or 
            "Subscribe to Group" functionality is selected).
        Return the user created or None.
        """
        from tendenci.apps.profiles.models import Profile
        emailfield = self.get_email_address()
        anonymous_creator = None

        if emailfield:
            user_list = User.objects.filter(email=emailfield).order_by('-last_login')
            if user_list:
                anonymous_creator = user_list[0]
            else:
                # Create a new user only if payment is involved or 
                # "Subscribe to Group" functionality selected
                if get_setting('module', 'forms', 'form_submission_create_user') or \
                         self.form.custom_payment or self.form.recurring_payment or \
                         self.fields.filter(field__field_function__in=["GroupSubscription",
                                                                       "GroupSubscriptionAuto"],
                                            ).exclude(value='').exists():
                    first_name = self.get_first_name()
                    last_name = self.get_last_name()
                    if not (first_name and last_name):
                        full_name = self.get_full_name()
                        if full_name:
                            name_list = full_name.split(" ", 1)
                            first_name = name_list[0]
                            last_name = name_list[1] if len(name_list) > 1 else ""

                    anonymous_creator = User(username=emailfield[:30], email=emailfield,
                                             first_name=first_name, last_name=last_name)
                    anonymous_creator.set_unusable_password()
                    anonymous_creator.is_active = False
                    anonymous_creator.save()
                    
                    anonymous_profile = Profile(user=anonymous_creator,
                                                owner=anonymous_creator,
                                                creator=anonymous_creator,
                                                phone=self.get_phone_number(),
                                                address=self.get_address(),
                                                company=self.get_company(),
                                                city=self.get_city(),
                                                region=self.get_region(),
                                                state=self.get_state(),
                                                zipcode=self.get_zipcode(),
                                                position_title=self.get_position_title(),
                                                referral_source=self.get_referral_source(),
                                                notes=self.get_notes(),
                                                )
                    anonymous_profile.save()

        return anonymous_creator
        


class FieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a user-built form.
    """

    entry = models.ForeignKey("FormEntry", related_name="fields", on_delete=models.CASCADE)
    field = models.ForeignKey("Field", related_name="field", on_delete=models.CASCADE)
    value = models.CharField(max_length=FIELD_MAX_LENGTH)

    class Meta:
        verbose_name = _("Form field entry")
        verbose_name_plural = _("Form field entries")
        app_label = 'forms'

    def __str__(self):
        return ('%s: %s' % (self.field.label, self.value))

    def include_in_email(self):
        widget = self.field.get_field_widget()
        field_class = self.field.get_field_class()
        if widget == 'tendenci.apps.forms_builder.forms.widgets.Description':
            return False
        if widget == 'tendenci.apps.forms_builder.forms.widgets.Header':
            return False
        if field_class == 'FileField':
            return False
        return True


class Pricing(models.Model):
    """
    Pricing options for custom payment forms.
    """
    form = models.ForeignKey('Form', on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    description = models.TextField(_("Pricing Description"), blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Leaving this field blank allows visitors to set their own price")
    )

    # Recurring payment fields
    taxable = models.BooleanField(default=False)
    tax_rate = models.DecimalField(blank=True, max_digits=5, decimal_places=4, default=0,
                                   help_text=_('Example: 0.0825 for 8.25%.'))
    billing_period = models.CharField(max_length=50, choices=BILLING_PERIOD_CHOICES,
                                        default='month')
    billing_frequency = models.IntegerField(default=1)
    num_days = models.IntegerField(default=0)
    due_sore = models.CharField(_("Billing cycle start or end date"), max_length=20,
                                   choices=DUE_SORE_CHOICES, default='start')
    has_trial_period = models.BooleanField(default=False)
    trial_period_days = models.IntegerField(default=0)
    trial_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0.0)

    class Meta:
        ordering = ["pk"]
        app_label = 'forms'

    def __str__(self):
        currency_symbol = get_setting("site", "global", "currencysymbol")
        if not currency_symbol:
            currency_symbol = '$'
        return "%s - %s%s" % (self.label, currency_symbol, self.price, )
