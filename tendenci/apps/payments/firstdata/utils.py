#import time
#import hashlib
from datetime import datetime
from django.conf import settings
#from django.http import Http404
from django.core.urlresolvers import reverse
from forms import FirstDataPaymentForm
from tendenci.core.payments.models import Payment
from tendenci.core.payments.utils import payment_processing_object_updates
from tendenci.core.payments.utils import log_payment, send_payment_notice

from tendenci.core.site_settings.utils import get_setting

currency_number_d = {'USD': '840',
                   'EUR': '978',
                   'GBP': '826',
                   'CHF': '756',
                   'CZK': '203',
                   'DKK': '208',
                   'JPY': '392',
                   'ZAR': '710',
                   'SEK': '752',
                   'CAD': '124'}

def prepare_firstdata_form(request, payment):
    chargetotal = "%.2f" % payment.amount
    #time_zone = get_setting("site", "global", 'defaulttimezone')
    #txndatetime = payment.create_dt.strftime('%Y:%m:%d-%H:%M:%S')
    #currency_code = get_setting("site", "global", 'currency')
    #if not currency_code: currency_code = 'USD'
    #currency = currency_number_d.get(currency_code, '840')

    # SHA1 hash
    #s = '%s%s%s%s%s' % (settings.MERCHANT_LOGIN, txndatetime, chargetotal, currency, settings.MERCHANT_TXN_KEY)
    #hash = hashlib.sha1(s).hexdigest()

    if request.user.is_authenticated():
        userid = request.user.id
    else:
        userid = 0

    params = {
              'storename':settings.MERCHANT_LOGIN,
              'mode':'payonly',
              'txntype':'sale',
              #'timezone': time_zone,
              #'txndatetime': txndatetime,
              #'hash': hash,
              #'currency': currency,
              'oid': "%s-%s" % (payment.id, datetime.now().strftime('%Y%m%d-%H%M%S')),
              'userid':userid,
              'bcountry':payment.country,
              #'objectguid':payment.guid,
              'paymentid':payment.id,
              'invoiceid':payment.invoice.id,
              'referurl': '%s%s' % (get_setting('site', 'global', 'siteurl'),
                                    reverse('payment.pay_online', args=[payment.invoice.id])),
              'chargetotal':chargetotal,
              'bname':'%s %s' % (payment.first_name, payment.last_name),
              'email':payment.email,
              'bcompany':payment.cust_id,
              'baddr1':payment.address,
              'baddr2':payment.address2,
              'bcity':payment.city,
              'bstate':payment.state,
              'fax':payment.fax,
              'phone':payment.phone,
              'shippingbypass':'true',
              'comments':payment.description,
              'responseSuccessURL': payment.response_page,
              'responseFailURL': payment.response_page,
        }
    form = FirstDataPaymentForm(initial=params)

    return form

def firstdata_thankyou_processing(request, response_d, **kwargs):
    from django.shortcuts import get_object_or_404

    paymentid = response_d.get('paymentid', 0)
    try:
        paymentid = int(paymentid)
    except:
        paymentid = 0
    payment = get_object_or_404(Payment, pk=paymentid)

    if payment.invoice.balance > 0:     # if balance==0, it means already processed
        payment_update_firstdata(request, response_d, payment)
        payment_processing_object_updates(request, payment)

        # log an event
        log_payment(request, payment)

        # send payment recipients notification
        send_payment_notice(request, payment)


    return payment

def payment_update_firstdata(request, response_d, payment, **kwargs):
    bname = response_d.get('bname', '')
    if bname:
        name_list = bname.split(' ')
        if len(name_list) >= 2:
            payment.first_name = name_list[0]
            payment.last_name = ' '.join(name_list[1:])
    payment.company = response_d.get('bcompany', '')
    payment.address = response_d.get('baddr1', '')
    payment.zip = response_d.get('bzip', '')
    payment.city = response_d.get('bcity', '')
    payment.state = response_d.get('bstate', '')
    payment.country = response_d.get('bcountry', '')
    payment.phone = response_d.get('phone', '')
    sname = response_d.get('sname', '')
    if sname:
        name_list = sname.split(' ')
        if len(name_list) >= 2:
            payment.ship_to_first_name = name_list[0]
            payment.ship_to_last_name = ' '.join(name_list[1:])
    payment.ship_to_address = response_d.get('saddr1', '')
    payment.ship_to_city = response_d.get('scity', '')
    payment.ship_to_state = response_d.get('sstate', '')
    payment.ship_to_country = response_d.get('scountry', '')

    payment.status_detail = (response_d.get('status', '')).lower()

    if payment.status_detail == 'approved':
        payment.response_code = '1'
        payment.response_subcode = '1'
        payment.response_reason_code = '1'
        # example of approval_code: 0097820000019564:YNAM:12345678901234567890123
        # http://www.firstdata.com/downloads/marketing-merchant/fd_globalgatewayconnect_usermanualnorthamerica.pdf
        payment.response_reason_text = response_d.get('approval_code', '')
        payment.trans_id = response_d.get('approval_code', '')
    else:
        payment.response_code = 0
        payment.response_reason_code = 0
        payment.response_reason_text = response_d.get('failReason', '')


    if payment.is_approved:
        payment.mark_as_paid()
        payment.save()
        payment.invoice.make_payment(request.user, payment.amount)
    else:
        if payment.status_detail == '':
            payment.status_detail = 'not approved'
        payment.save()
