import re
from datetime import datetime
from django.conf import settings
from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.forms_builder.forms.models import FormEntry, FieldEntry
from tendenci.apps.base.utils import escape_csv

def generate_admin_email_body(entry, form_for_form, user=None):
    """
        Generates the email body so that is readable
    """
    context = {}
    site_url = get_setting('site', 'global', 'siteurl')
#     if not user or user.is_anonymous or not user.is_active:
#         template = get_template('forms/admin_email_content_text.html')
#     else:
    template = get_template('forms/admin_email_content.html')

    # fields to loop through in the template
    context['fields'] = entry.entry_fields()
    # media_url necessary for file upload fields
    context['site_url'] = site_url
    context['media_url'] = site_url + settings.MEDIA_URL
    # form details to show in the email
    context['form'] = entry.form
    context['entry'] = entry
    context['custom_price'] = form_for_form.cleaned_data.get('custom_price')
    output = template.render(context=context)

    return output


def generate_submitter_email_body(entry, form_for_form):
    """
        Generates the email body so that is readable
    """
    context = {}
    template = get_template('forms/submitter_email_content.html')

    context['form'] = entry.form
    context['entry'] = entry
    context['fields'] = entry.entry_fields()
    context['custom_price'] = form_for_form.cleaned_data.get('custom_price')
    output = template.render(context=context)

    return output


def generate_email_subject(form, form_entry):
    """
        Generates email subject from subject template
    """
    if form.subject_template:
        subject = form.subject_template
        field_entries = form_entry.entry_fields()
        for field_entry in field_entries:
            label = field_entry.field.label
            value = field_entry.value
            # removes parens and asterisks so they don't break the re compile.
            label = re.sub(r'[\*()]', '', label)
            if not value:
                value = ''
                p = re.compile(r'(-\s+)?\[%s\]' % label, re.IGNORECASE)
            else:
                p = re.compile(r'\[%s\]' % label, re.IGNORECASE)
            subject = p.sub(value.replace('\\', ''), subject)

        # title
        p = re.compile(r'\[title\]', re.IGNORECASE)
        subject = p.sub(form.title, subject)

        # replace those brackets with blank string
        p = re.compile(r'(-\s+)?\[[\d\D\s\S\w\W]*?\]')
        subject = p.sub('', subject)

    else:
        subject = "%s:" % (form.title)
        if form_entry.get_first_name():
            subject = "%s %s" % (subject, form_entry.get_first_name())
        if form_entry.get_last_name():
            subject = "%s %s" % (subject, form_entry.get_last_name())
        if form_entry.get_full_name():
            subject = "%s %s" % (subject, form_entry.get_full_name())
        if form_entry.get_phone_number():
            subject = "%s - %s" % (subject, form_entry.get_phone_number())
        if form_entry.get_email_address():
            subject = "%s - %s" % (subject, form_entry.get_email_address())

    return subject


def make_invoice_for_entry(entry, **kwargs):
    """
    Create an invoice for a Form Entry.
    """

    price = entry.pricing.price
    if price is None:
        price = kwargs.get('custom_price')
    now = datetime.now()

    inv = Invoice()
    inv.title = "%s Invoice" % (entry.form.title)
    inv.object_type = ContentType.objects.get(app_label=entry._meta.app_label, model=entry._meta.model_name)
    inv.object_id = entry.id
    inv.subtotal = price
    inv.total = price
    inv.balance = price
    inv.due_date = now
    inv.ship_date = now

    tax = 0
    if entry.pricing and entry.pricing.taxable:
        tax = price * entry.pricing.tax_rate
        total = tax + price
        inv.tax = tax
        inv.subtotal = total
        inv.total = total
        inv.balance = total

    if entry.creator and not entry.creator.is_anonymous:
        inv.set_owner(entry.creator)

    inv.save()

    return inv

def update_invoice_for_entry(invoice, form):
    """
    Update invoice for an entry based on a form.
    """
    inv = invoice
    # field to be populated to invoice
    inv.bill_to =  form.cleaned_data['first_name'] + ' ' + form.cleaned_data['last_name']
    inv.bill_to_first_name = form.cleaned_data['first_name']
    inv.bill_to_last_name = form.cleaned_data['last_name']
    inv.bill_to_company = form.cleaned_data['company']
    inv.bill_to_address = form.cleaned_data['address']
    inv.bill_to_city = form.cleaned_data['city']
    inv.bill_to_state =  form.cleaned_data['state']
    inv.bill_to_zip_code = form.cleaned_data['zip_code']
    inv.bill_to_country = form.cleaned_data['country']
    inv.bill_to_phone = form.cleaned_data['phone']
    inv.bill_to_email = form.cleaned_data['email']
    inv.message = 'Thank You.'
    inv.status = True
    inv.estimate = True
    inv.status_detail = 'estimate'
    inv.save()


def form_entries_to_csv_writer(csv_writer, form):
    """
    Write form entries to csv_writer.
    """
    columns = []
    field_indexes = {}
    file_field_ids = []
    site_url = get_setting('site', 'global', 'siteurl')
    for field in form.fields.all().order_by('position', 'id'):
        columns.append(field.label)
        field_indexes[field.id] = len(field_indexes)
        if field.field_type == "FileField":
            file_field_ids.append(field.id)
    entry_time_name = FormEntry._meta.get_field("entry_time").verbose_name
    columns.append(str(entry_time_name))
    if form.custom_payment:
        columns.append(str("Pricing"))
        columns.append(str("Price"))
        columns.append(str("Payment Method"))
    csv_writer.writerow(columns)
    # Loop through each field value order by entry, building up each
    # entry as a row.
    entries = FormEntry.objects.filter(form=form).order_by('pk')
    for entry in entries:
        values = FieldEntry.objects.filter(entry=entry)
        row = [""] * len(columns)
        entry_time = entry.entry_time.strftime("%Y-%m-%d %H:%M:%S")

        if form.custom_payment:
            if entry.pricing:
                row[-4] = entry_time
                row[-3] = entry.pricing.label
                if not entry.pricing.price:
                    row[-2] = entry.custom_price
                else:
                    row[-2] = entry.pricing.price
            row[-1] = entry.payment_method
        else:
            row[-1] = entry_time

        for field_entry in values:
            value = escape_csv(field_entry.value)
            # Create download URL for file fields.
#             if field_entry.field_id in file_field_ids:
#                 url = reverse("admin:forms_form_file", args=(field_entry.id,))
#                 value = '{site_url}{url}'.format(site_url=site_url, url=url)
            # Only use values for fields that currently exist for the form.
            try:
                row[field_indexes[field_entry.field_id]] = value
            except KeyError:
                pass
        # Write out the row.
        csv_writer.writerow(row)

