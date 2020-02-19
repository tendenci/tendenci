from builtins import str
import re
#from south.modelsinspector import add_introspection_rules

from django.forms import fields, ValidationError
from django.db.models import CharField
from django.utils.translation import ugettext_lazy as _
from django.db import models
import simplejson
from django.core import exceptions
from django_countries import countries as COUNTRIES

from tendenci.apps.base import forms
from tendenci.apps.base.widgets import EmailVerificationWidget, PriceWidget
from tendenci.apps.site_settings.utils import get_setting


# # introspection rules for south migration for the slugfield
# add_introspection_rules([], [r'^tendenci\.apps\.base\.fields\.SlugField'])
# add_introspection_rules([], [r'^tendenci\.apps\.base\.fields\.DictField'])


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


class DictField(models.TextField):
    """
    A dictionary field
    """

    def to_python(self, value):
        if not value:
            return {}

        if isinstance(value, str):
            try:
                return simplejson.loads(value)
            except (ValueError, TypeError):
                raise exceptions.ValidationError(
                        self.error_messages['invalid'])

        if isinstance(value, dict):
            return value

        return {}

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def get_prep_value(self, value):
        if isinstance(value, dict):
            return simplejson.dumps(value)

        if isinstance(value, str):
            return value

        return ''


class EmailVerificationField(fields.MultiValueField):
    # widget = EmailVerificationWidget

    def __init__(self, attrs=None, *args, **kwargs):
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
        super(EmailVerificationField, self).__init__(all_fields, widget=EmailVerificationWidget(attrs={'class': 'form-control'}), label=label, *args, **kwargs)

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

        initial_choices = ()
        exclude_list = []

        initial_choices_keys = get_setting('site', 'global', 'countrylistinitialchoices')
        if initial_choices_keys and initial_choices_keys != u'[]':
            initial_choices =  ((name, name) for key, name in list(COUNTRIES) if key in initial_choices_keys)
            exclude_list = initial_choices_keys

        initial_choices = tuple(initial_choices) + (('','-----------'),)
        countries = ((name,name) for key,name in list(COUNTRIES) if key not in exclude_list)
        self.choices = initial_choices + tuple(countries)
        self.initial = ''


class PriceField(fields.DecimalField):

    def __init__(self, max_value=None, min_value=None, max_digits=None, decimal_places=None, *args, **kwargs):
        super(PriceField, self).__init__(*args, max_value=max_value, min_value=min_value, max_digits=max_digits, decimal_places=decimal_places, **kwargs)
        self.widget = PriceWidget()

    def clean(self, value):
        comma_setting = get_setting('site', 'global', 'allowdecimalcommas')
        if comma_setting and value is not None and ',' in value:
            comma_validator = re.compile(r'^[0-9]{1,3}(,[0-9]{3})*(\.[0-9]+)?$')
            if comma_validator.match(value):
                value = re.sub(r',', '', value)
            else:
                raise ValidationError(self.error_messages['invalid'])

        return super(PriceField, self).clean(value)
