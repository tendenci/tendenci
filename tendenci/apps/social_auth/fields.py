from builtins import str
from django.core.exceptions import ValidationError
from django.db import models
import simplejson
from django.utils.encoding import smart_str
# from south.modelsinspector import add_introspection_rules
#
# # introspection rules for south migration for the JSONField
# add_introspection_rules([], [r'^tendenci\.apps\.social_auth\.fields\.JSONField'])


class JSONField(models.TextField):
    """Simple JSON field that stores python structures as JSON strings
    on database.
    """

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return None
        if isinstance(value, str):
            try:
                return simplejson.loads(value)
            except Exception as e:
                raise ValidationError(str(e))
        else:
            return value

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        super(JSONField, self).validate(value, model_instance)
        try:
            return simplejson.loads(value)
        except Exception as e:
            raise ValidationError(str(e))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return simplejson.dumps(value)
        except Exception as e:
            raise ValidationError(str(e))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return smart_str(self.get_prep_value(self.value_from_obj(obj)))
