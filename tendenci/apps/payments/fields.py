from django import forms


class PaymentmentMethodHumanNameMixin:
    def label_from_instance(self, obj):
        return obj.human_name


class PaymentMethodModelChoiceField(PaymentmentMethodHumanNameMixin, forms.ModelChoiceField):
    pass


class PaymentMethodModelMultipleChoiceField(PaymentmentMethodHumanNameMixin, forms.ModelMultipleChoiceField):
    pass
