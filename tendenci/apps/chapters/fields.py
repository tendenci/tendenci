from django import forms
from django.core.exceptions import ValidationError


class ChapterMembershipTypeModelChoiceField(forms.ModelChoiceField):
    renew_mode = False
    chapter = None

    def label_from_instance(self, obj):
        return obj.get_price_display(renew_mode=self.renew_mode,
                                     chapter=self.chapter)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            if type(value) == list:
                value = value[0]
            value = self.queryset.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value