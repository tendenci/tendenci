from datetime import datetime
from django import forms
from django.utils.translation import gettext_lazy as _
from tendenci.apps.payments.models import Payment, PaymentMethod


class MarkAsPaidForm(forms.ModelForm):
    payment_method = forms.CharField(max_length=20)

    submit_dt = forms.SplitDateTimeField(
        label=_('Submit Date and Time'),
        initial=datetime.now())

    class Meta:
        model = Payment
        fields = (
            'amount',
            'payment_method',
            'check_number',
            'submit_dt',
        )

    def __init__(self, *args, **kwargs):
        super(MarkAsPaidForm, self).__init__(*args, **kwargs)
        self.fields['payment_method'].widget = forms.Select(
            choices=PaymentMethod.objects.filter().values_list(
                    'machine_name', 'human_name').exclude())

    def save(self, user, invoice, *args, **kwargs):
        """
        Save payment, bind invoice instance.
        Set payment fields (e.g. name, description)
        """
        instance = super(MarkAsPaidForm, self).save(*args, **kwargs)

        instance.method = self.cleaned_data['payment_method']

        instance.invoice = invoice
        instance.first_name = invoice.bill_to_first_name
        instance.last_name = invoice.bill_to_last_name
        instance.email = invoice.bill_to_email
        instance.status_detail = 'approved'

        instance.creator = user
        instance.creator_username = user.username
        instance.owner = user
        instance.owner_username = user.username

        instance.save()

        invoice_object = invoice.get_object()

        if invoice_object:
            if hasattr(invoice_object, 'get_payment_description'):
                instance.description = invoice_object.get_payment_description(invoice)
            if not instance.description:
                instance.description = 'Tendenci Invoice {} for {}({})'.format(
                    instance.pk, invoice_object, invoice_object.pk)

        return instance


class PaymentSearchForm(forms.Form):
    SEARCH_CRITERIA_CHOICES = (
        ('', _('SELECT ONE')),
        ('first_name', _('First Name')),
        ('last_name', _('Last Name')),
        ('amount', _('Amount')),
        ('owner_username', _('Owner Username')),
        ('id', _('Payment ID')),
        ('invoice__id', _('Invoice ID')),
        ('trans_id', _('Transaction ID')),
        ('auth_code', _('Authorization Code'))
    )
    SEARCH_METHOD_CHOICES = (
        ('starts_with', _('Starts With')),
        ('contains', _('Contains')),
        ('exact', _('Exact')),
    )

    search_criteria = forms.ChoiceField(choices=SEARCH_CRITERIA_CHOICES,
                                        required=False)
    search_text = forms.CharField(max_length=100, required=False)
    search_method = forms.ChoiceField(choices=SEARCH_METHOD_CHOICES,
                                        required=False)
