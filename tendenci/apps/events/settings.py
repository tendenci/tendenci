from django.utils.translation import ugettext_lazy as _

FIELD_MAX_LENGTH = 2000
LABEL_MAX_LENGTH = 255

FIELD_TYPE_CHOICES = (
    ("CharField", _("Text")),
    ('DecimalField', _('Number')),
    ("CharField/django.forms.Textarea", _("Paragraph Text")),
    ("BooleanField", _("Checkbox")),
    ("ChoiceField/django.forms.RadioSelect", _("Single-select - Radio Button")),
    ("ChoiceField", _("Single-select - From a List")),
    ("MultipleChoiceField/django.forms.CheckboxSelectMultiple", _("Multi-select - Checkboxes")),
    ("MultipleChoiceField", _("Multi-select - From a List")),
    ("EmailVerificationField", _("Email")),
    ("DateField/django.forms.widgets.SelectDateWidget", _("Date")),
    ("DateTimeField", _("Date/time")),
    ("CharField/tendenci.apps.forms_builder.forms.widgets.Description", _("Description")),
    ("CharField/tendenci.apps.forms_builder.forms.widgets.Header", _("Section Heading")),
)

USER_FIELD_CHOICES = (
    ('first_name', _('First Name')),
    ('last_name', _('Last Name')),
    ('mail_name', _('Mailing Name')),
    ('address', _('Address')),
    ('city', _('City')),
    ('state', _('State')),
    ('zip', _('Zip Code')),
    ('country', _('Country')),
    ('phone', _('Phone')),
    ('email', _('Email')),
    ('position_title', _('Position Title')),
    ('company_name', _('Company Name')),
    ('meal_option', _('Meal Option')),
    ('comments', _('Comments')) )

FIELD_FUNCTIONS = (
    ("GroupSubscription", _("Subscribe to Group")),
)
