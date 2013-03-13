from django import forms
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.invoices.models import Invoice
from tendenci.addons.events.models import Event


class AdminNotesForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('admin_notes',
                  )


class AdminAdjustForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('variance',
                  'variance_notes',
                  )


class InvoiceSearchForm(forms.Form):
    INVOICE_TYPE_CHOICES = (
        ('', '-----------------'),
        ('events', 'events'),
        ('memberships', 'memberships'),
        ('jobs', 'jobs')
    )
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    start_dt = forms.DateField(label=_('From'), required=False)
    end_dt = forms.DateField(label=_('To'), required=False)

    invoice_type = forms.ChoiceField(label=_("Invoice Type"), required=False, choices=INVOICE_TYPE_CHOICES)
    event = forms.ModelChoiceField(queryset=Event.objects.all(),
                                   label=_("Event "),
                                   required=False,
                                   empty_label='All Events')
    event_id = forms.ChoiceField(label=_('Event ID'), required=False, choices=[])

    def __init__(self, *args, **kwargs):
        super(InvoiceSearchForm, self).__init__(*args, **kwargs)

        # Set start date and end date
        if self.fields.get('start_dt'):
            self.fields.get('start_dt').widget.attrs = {
                'class': 'datepicker',
            }
        if self.fields.get('end_dt'):
            self.fields.get('end_dt').widget.attrs = {
                'class': 'datepicker',
            }

        # Set invoice type choices
        invoices = Invoice.objects.all().distinct('object_type__app_label')
        invoice_choices = [('', '-----------------')]
        for entry in invoices:
            if entry.object_type:
                invoice_choices.append((entry.object_type.app_label, entry.object_type.app_label))
        self.fields['invoice_type'].choices = invoice_choices

        # Set event_id choices
        choices = [('', 'All events')]
        events = Event.objects.all()  # .filter(registration__invoice__isnull=False)
        for event_obj in events:
            choices.append((event_obj.pk, event_obj.pk))
        self.fields['event_id'].choices = choices
