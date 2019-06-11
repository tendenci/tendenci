from datetime import datetime, date, time
import time as ttime
from io import BytesIO
from xhtml2pdf import pisa

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.urls import reverse
from django.template.loader import render_to_string
from django.template.loader import get_template

from tendenci.apps.invoices.models import Invoice
from tendenci.apps.base.utils import UnicodeWriter
from tendenci.apps.emails.models import Email
from tendenci.apps.site_settings.utils import get_setting

def invoice_pdf(request, invoice):
    obj = invoice.get_object()
    if obj:
        obj_name = obj._meta.verbose_name
    else:
        obj_name = ''

    payment_method = ""
    if invoice.balance <= 0:
        if invoice.payment_set:
            payment_set = invoice.payment_set.order_by('-id')
            if payment_set:
                payment = payment_set[0]
                payment_method = payment.method
    tmp_total = 0
    if invoice.variance and invoice.variance != 0:
        tmp_total = invoice.subtotal
        if invoice.tax:
            tmp_total += invoice.tax
        if invoice.shipping:
            tmp_total += invoice.shipping
        if invoice.shipping_surcharge:
            tmp_total += invoice.shipping_surcharge
        if invoice.box_and_packing:
            tmp_total += invoice.box_and_packing

    template_name="invoices/pdf.html"
    template = get_template(template_name)
    html  = template.render(context={
                             'invoice': invoice,
                             'obj_name': obj_name,
                             'payment_method': payment_method,
                             'tmp_total': tmp_total,
                             'pdf_version': True,
                            }, request=request)
    result = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    #pisa.pisaDocument(BytesIO(html.encode("utf-8")), result,
    #                  path=get_setting('site', 'global', 'siteurl'))
    return result

def process_invoice_export(start_dt=None, end_dt=None,
                           identifier=u'', user_id=0):

    fields = ['id',
              'guid',
              'object_type',
              'object_id',
              'title',
              'tender_date',
              'bill_to',
              'bill_to_first_name',
              'bill_to_last_name',
              'bill_to_company',
              'bill_to_address',
              'bill_to_city',
              'bill_to_state',
              'bill_to_zip_code',
              'bill_to_country',
              'bill_to_phone',
              'bill_to_fax',
              'bill_to_email',
              'ship_to',
              'ship_to_first_name',
              'ship_to_last_name',
              'ship_to_company',
              'ship_to_address',
              'ship_to_city',
              'ship_to_state',
              'ship_to_zip_code',
              'ship_to_country',
              'ship_to_phone',
              'ship_to_fax',
              'ship_to_email',
              'ship_to_address_type',
              'receipt',
              'gift',
              'arrival_date_time',
              'greeting',
              'instructions',
              'po',
              'terms',
              'due_date',
              'ship_date',
              'ship_via',
              'fob',
              'project',
              'other',
              'message',
              'subtotal',
              'shipping',
              'shipping_surcharge',
              'box_and_packing',
              'tax_exempt',
              'tax_exemptid',
              'tax_rate',
              'taxable',
              'tax',
              'variance',
              'discount_amount',
              'total',
              'payments_credits',
              'balance',
              'disclaimer',
              'variance_notes',
              'admin_notes',
              'create_dt',
              'update_dt',
              'creator',
              'creator_username',
              'owner',
              'owner_username',
              'status_detail']

    identifier = identifier or int(ttime.time())
    file_name_temp = 'export/invoices/%s_temp.csv' % identifier

    with default_storage.open(file_name_temp, 'wb') as csvfile:
        csv_writer = UnicodeWriter(csvfile, encoding='utf-8')
        csv_writer.writerow(fields)

        invoices = Invoice.objects.filter(status=True,
                                          update_dt__gte=start_dt,
                                          update_dt__lte=end_dt)
        for invoice in invoices:
            items_list = []
            for field_name in fields:
                item = getattr(invoice, field_name)
                if item is None:
                    item = ''
                if item:
                    if isinstance(item, datetime):
                        item = item.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(item, date):
                        item = item.strftime('%Y-%m-%d')
                    elif isinstance(item, time):
                        item = item.strftime('%H:%M:%S')
                items_list.append(item)
            csv_writer.writerow(items_list)

    # rename the file name
    file_name = 'export/invoices/%s.csv' % identifier
    default_storage.save(file_name, default_storage.open(file_name_temp, 'rb'))

    # delete the temp file
    default_storage.delete(file_name_temp)

    # notify user that export is ready to download
    [user] = User.objects.filter(pk=user_id)[:1] or [None]
    if user and user.email:
        download_url = reverse('invoice.export_download', args=[identifier])

        site_url = get_setting('site', 'global', 'siteurl')
        site_display_name = get_setting('site', 'global', 'sitedisplayname')
        parms = {
            'download_url': download_url,
            'user': user,
            'site_url': site_url,
            'site_display_name': site_display_name,
            'start_dt': start_dt,
            'end_dt': end_dt}

        subject = render_to_string(
            template_name='invoices/notices/export_ready_subject.html', context=parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            template_name='invoices/notices/export_ready_body.html', context=parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)
        email.send()
