from datetime import datetime, date, time
import time as ttime
import csv

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.encoding import smart_str

from tendenci.apps.invoices.models import Invoice
from tendenci.core.base.utils import UnicodeWriter
from tendenci.core.emails.models import Email
from tendenci.core.site_settings.utils import get_setting


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
                    elif isinstance(item, basestring):
                        item = item.encode("utf-8")
                item = smart_str(item).decode('utf-8')
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
            'invoices/notices/export_ready_subject.html', parms)
        subject = subject.strip('\n').strip('\r')

        body = render_to_string(
            'invoices/notices/export_ready_body.html', parms)

        email = Email(
            recipient=user.email,
            subject=subject,
            body=body)
        email.send()

