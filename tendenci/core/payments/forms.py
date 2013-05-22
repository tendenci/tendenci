from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from tendenci.core.base.fields import SplitDateTimeField
from tendenci.core.payments.models import Payment, PaymentMethod

PAYMENT_METHODS = PaymentMethod.objects.filter().values_list(
    'machine_name', 'human_name').exclude()


class MarkAsPaidForm(forms.ModelForm):

    payment_method = forms.CharField(
        max_length=20,
        widget=forms.Select(choices=PAYMENT_METHODS))

    submit_dt = SplitDateTimeField(
        label=_('Submit Date and Time'),
        initial=datetime.now())

    class Meta:
        model = Payment
        fields = (
            'amount',
            'payment_method',
            'submit_dt',
        )

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

        if hasattr(invoice_object, 'get_payment_description'):
            instance.description = invoice_object.get_payment_description(invoice)

        if not instance.description:
            instance.description = 'Tendenci Invoice {} for {}({})'.format(
                instance.pk, invoice_object, invoice_object.pk)

        return instance
