from django import forms
from django.db.models.fields import CharField, DecimalField
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
        ('events', _('events')),
        ('memberships', _('memberships')),
        ('jobs', _('jobs'))
    )
    SEARCH_METHOD_CHOICES = (
        ('starts_with', _('Starts With')),
        ('contains', _('Contains')),
        ('exact', _('Exact')),
    )
    TENDERED_CHOICES = (
        ('', _('Show All')),
        ('tendered', _('Tendered')),
        ('estimate', _('Estimate')),
        ('void', _('Void')),
    )
    BALANCE_CHOICES = (
        ('', _('Show All')),
        ('0', _('Zero Balance')),
        ('1', _('Non-zero Balance')),
    )
    search_criteria = forms.ChoiceField(choices=[],
                                        required=False)
    search_text = forms.CharField(max_length=100, required=False)
    search_method = forms.ChoiceField(choices=SEARCH_METHOD_CHOICES,
                                        required=False)
    start_dt = forms.DateField(label=_('From'), required=False)
    end_dt = forms.DateField(label=_('To'), required=False)

    start_amount = forms.DecimalField(required=False)
    end_amount = forms.DecimalField(required=False)

    tendered = forms.ChoiceField(choices=TENDERED_CHOICES,
                                        required=False)
    balance = forms.ChoiceField(choices=BALANCE_CHOICES,
                                        required=False)

    last_name = forms.CharField(label=_('Billing Last Name'),
                                max_length=100, required=False)

    invoice_type = forms.ChoiceField(label=_("Invoice Type"), required=False, choices=INVOICE_TYPE_CHOICES)
    event = forms.ModelChoiceField(queryset=Event.objects.all(),
                                   label=_("Event "),
                                   required=False,
                                   empty_label=_('All Events'))
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

        # Set search criteria choices
        criteria_choices = [('', _('SELECT ONE'))]
        criteria_choices.append(('id', _('ID')))
        for field in Invoice._meta.fields:
            if isinstance(field, CharField) or isinstance(field, DecimalField):
                if not field.name.startswith('bill_to') and not field.name.startswith('ship_to'):
                    criteria_choices.append((field.name, field.verbose_name))
        criteria_choices.append(('owner_id', _('owner')))
        self.fields['search_criteria'].choices = criteria_choices

        # Set invoice type choices
        invoices = Invoice.objects.all().distinct('object_type__app_label')
        invoice_choices = [('', '-----------------')]
        for entry in invoices:
            if entry.object_type:
                invoice_choices.append((entry.object_type.app_label, entry.object_type.app_label))
        self.fields['invoice_type'].choices = invoice_choices

        # Set event_id choices
        choices = [('', _('All events'))]
        events = Event.objects.all()  # .filter(registration__invoice__isnull=False)
        for event_obj in events:
            choices.append((event_obj.pk, event_obj.pk))
        self.fields['event_id'].choices = choices
