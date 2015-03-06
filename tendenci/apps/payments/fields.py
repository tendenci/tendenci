from django import forms


class PaymentMethodModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.human_name
