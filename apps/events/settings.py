from django.utils.translation import ugettext, ugettext_lazy as _


FIELD_MAX_LENGTH = 2000
LABEL_MAX_LENGTH = 255

FIELD_TYPE_CHOICES = (
    ("CharField", _("Text")),
    ("CharField/django.forms.Textarea", _("Paragraph Text")),
    ("BooleanField", _("Checkbox")),
    ("ChoiceField", _("Choose from a list")),
    ("MultipleChoiceField", _("Multi select")),
    ("EmailField", _("Email")),
    ("DateField/django.forms.extras.SelectDateWidget", _("Date")),
    ("DateTimeField", _("Date/time")),
    ("CharField/forms_builder.forms.widgets.Description", _("Description")),
    ("CharField/forms_builder.forms.widgets.Header", _("Section Heading")),
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
                      )