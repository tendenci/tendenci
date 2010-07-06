from time import strptime, strftime

from django.forms import fields
from django.db.models import CharField
from django.utils.translation import ugettext_lazy as _

from base import forms
from base.widgets import SplitDateTimeWidget

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
                raise forms.ValidationError("Field is missing data.")
            input_time = strptime("%s" % (data_list[1]), "%I:%M %p")
            datetime_string = "%s %s" % (data_list[0], strftime('%H:%M', input_time))
            return datetime_string
        return None