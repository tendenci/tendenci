import re
from time import strptime, strftime
from south.modelsinspector import add_introspection_rules

from django.forms import fields, ValidationError
from django.db.models import CharField
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils import simplejson
from django.core import exceptions
from django_countries.countries import COUNTRIES

from tendenci.core.base import forms
from tendenci.core.base.widgets import SplitDateTimeWidget, EmailVerificationWidget, PriceWidget
from tendenci.core.site_settings.utils import get_setting


# introspection rules for south migration for the slugfield
add_introspection_rules([], ['^tendenci\.core\.base\.fields\.SlugField'])
add_introspection_rules([], ['^tendenci\.core\.base\.fields\.DictField'])


class SlugField(CharField):
    """
        New slug field that uses a different set of validations
        Straight copy from django with modifications
    """
    description = _("String (up to %(max_length)s)")
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 100)
        # Set db_index=True unless it's been set manually.
        if 'db_index' not in kwargs:
            kwargs['db_index'] = True
        super(SlugField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "SlugField"

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.SlugField}
        defaults.update(kwargs)
        return super(SlugField, self).formfield(**defaults)

class SplitDateTimeField(fields.MultiValueField):
    """
        Custom split date time widget
        Modified version of http://www.copiesofcopies.org/webl/?p=81
    """
    widget = SplitDateTimeWidget

    def __init__(self, *args, **kwargs):
        """
        Have to pass a list of field types to the constructor, else we
        won't get any data to our compress method.
        """
        all_fields = (
            fields.CharField(max_length=10),
            fields.CharField(max_length=8),
            )
        super(SplitDateTimeField, self).__init__(all_fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Takes the values from the MultiWidget and passes them as a
        list to this function. This function needs to compress the
        list into a single object to save.
        """
        if data_list:
            if not (data_list[0] and data_list[1]):
                raise ValidationError(_("Field is missing data."))
            try:
                input_time = strptime("%s" % (data_list[1]), "%I:%M %p")
                datetime_string = "%s %s" % (data_list[0], strftime('%H:%M', input_time))
            except:
                raise ValidationError(_("Time Format is incorrect. Must be Hour:Minute AM|PM"))
            return datetime_string
        return None


class DictField(models.TextField):
    """
    A dictionary field
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if not value:
            return {}

        if isinstance(value, basestring):
            try:
                return simplejson.loads(value)
            except (ValueError, TypeError):
                raise exceptions.ValidationError(
                        self.error_messages['invalid'])

        if isinstance(value, dict):
            return value

        return {}

    def get_prep_value(self, value):
        if isinstance(value, dict):
            return simplejson.dumps(value)

        if isinstance(value, basestring):
            return value

        return ''


class EmailVerificationField(fields.MultiValueField):
    widget = EmailVerificationWidget

    def __init__(self, *args, **kwargs):
        """
        Have to pass a list of field types to the constructor, else we
        won't get any data to our compress method.
        """
        all_fields = (
            fields.EmailField(max_length=75),
            fields.EmailField(max_length=75, label=_("Verfiy Email Address")),
            )
        label = kwargs.pop('label', '') + ' (Enter twice to verify)'
        label = _(label)
        super(EmailVerificationField, self).__init__(all_fields, label=label, *args, **kwargs)

    def compress(self, data_list):
        """
        Takes the values from the MultiWidget and passes them as a
        list to this function. This function needs to compress the
        list into a single object to save.
        """
        if data_list:
            if not (data_list[0] and data_list[1]):
                raise ValidationError(_("Please enter the email twice to verify."))
            if data_list[0] != data_list[1]:
                raise ValidationError(_("Please enter the same email address."))
            email_data = "%s" % (data_list[0])
            return email_data
        return ''


class CountrySelectField(fields.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)

        exclude_list = ['GB', 'US', 'CA']
        countries = ((name,name) for key,name in COUNTRIES if key not in exclude_list)
        initial_choices = (('United States', _('United States')),
                           ('Canada', _('Canada')),
                           ('United Kingdom', _('United Kingdom')),
                           ('','-----------'))
        self.choices = initial_choices + tuple(countries)
        self.initial = 'United States'


class PriceField(fields.DecimalField):

    def __init__(self, max_value=None, min_value=None, max_digits=None, decimal_places=None, *args, **kwargs):
        super(PriceField, self).__init__(max_value, min_value, max_digits, decimal_places, *args, **kwargs)
        self.widget = PriceWidget()

    def clean(self, value):
        comma_setting = get_setting('site', 'global', 'allowdecimalcommas')
        if comma_setting and ',' in value:
            comma_validator = re.compile(r'^[0-9]{1,3}(,[0-9]{3})*(\.[0-9]+)?$')
            if comma_validator.match(value):
                value = re.sub(',', '', value)
            else:
                raise ValidationError(self.error_messages['invalid'])

        return super(PriceField, self).clean(value)
