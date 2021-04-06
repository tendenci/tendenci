from datetime import date, datetime
from django import forms
from django.db.models.fields import CharField, DecimalField
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.invoices.models import Invoice
from tendenci.apps.events.models import Event
from tendenci.apps.emails.models import Email
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.base.forms import FormControlWidgetMixin


class EmailInvoiceForm(FormControlWidgetMixin, forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%;padding:5px 0;'}))
    recipient = forms.EmailField(label=_('Recipient'))
    cc = forms.EmailField(label=_('CC'), required=False)
    body = forms.CharField(widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Email._meta.app_label,
        'storme_model':Email._meta.model_name.lower()}),
        label=_('Email Content'))
    attachment = forms.BooleanField(label=_('Attach PDF?'), required=False, initial=True)

    class Meta:
        model = Email
        fields = ('subject', 'recipient', 'cc', 'body', )

    def __init__(self, *args, **kwargs):
        super(EmailInvoiceForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0

        self.fields['recipient'].widget.attrs['placeholder'] = _('Email Address')
        self.fields['cc'].widget.attrs['placeholder'] = _('Email Address')


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


class AdminVoidForm(FormControlWidgetMixin, forms.ModelForm):
    cancle_registration = forms.BooleanField(label=_('Cancel the corresponding event registration'),
                                             required=False, initial=False)
    delete_membership = forms.BooleanField(label=_('Delete the corresponding memberships'),
                                             required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(AdminVoidForm, self).__init__(*args, **kwargs)
        self.fields['void_reason'].widget.attrs.update({'cols': 30, 'rows': 4})

    class Meta:
        model = Invoice
        fields = ('void_reason',
                  )


class ReportsOverviewForm(FormControlWidgetMixin, forms.Form):
    entity = forms.ChoiceField(choices=(), required=False)
    start_dt = forms.DateField(label=_('From'), required=False)
    end_dt = forms.DateField(label=_('To'), required=False,)

    def __init__(self, data, **kwargs):
        initial = kwargs.get('initial', {})
        if not data:
            data = {**initial, **data}
        super(ReportsOverviewForm, self).__init__(data, **kwargs)
        self.fields['start_dt'].widget.attrs['class'] += ' datepicker'
        self.fields['end_dt'].widget.attrs['class'] += ' datepicker'
        entities = Invoice.objects.values('entity__id', 'entity__entity_name').order_by('entity__entity_name').distinct('entity__entity_name')
        self.fields['entity'].choices = [('', _('ALL Entities')),] + [(item['entity__id'], item['entity__entity_name']) for item in entities]


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
    object_type_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

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
            else:
                invoice_choices.append(('unknown', _('Unknown')))
        self.fields['invoice_type'].choices = invoice_choices

        # Set event_id choices
        choices = [('', _('All events'))]
        events = Event.objects.all()  # .filter(registration__invoice__isnull=False)
        for event_obj in events:
            choices.append((event_obj.pk, event_obj.pk))
        self.fields['event_id'].choices = choices
