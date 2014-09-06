import urllib
import urllib2
import cgi
from decimal import Decimal

from django.conf import settings
from django.core.urlresolvers import reverse
from django import forms
from django.http import Http404
from django.shortcuts import get_object_or_404

from tendenci.apps.payments.paypal.forms import PayPalPaymentForm
from tendenci.apps.payments.models import Payment
from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.payments.utils import log_payment, send_payment_notice
from tendenci.apps.site_settings.utils import get_setting


def prepare_paypal_form(request, payment):
    amount = "%.2f" % payment.amount
    image_url = get_setting("site", "global", "MerchantLogo")
    site_url = get_setting('site', 'global', 'siteurl')
    notify_url = '%s/%s' % (site_url, reverse('paypal.ipn'))
    currency_code = get_setting('site', 'global', 'currency')
    if not currency_code:
        currency_code = 'USD'
    params = {
              'business': settings.PAYPAL_MERCHANT_LOGIN,
              'image_url': image_url,
              'amount': amount,
              'notify_url': notify_url,
              'currency_code': currency_code,
              'invoice': payment.id,
              'item_name': payment.description,
              'first_name': payment.first_name,
              'last_name': payment.last_name,
              'email': payment.email,
              'address1': payment.address,
              'address2': payment.address2,
              'city': payment.city,
              'state': payment.state,
              'country': payment.country,
              'zip': payment.zip,
              'night_phone_a': payment.phone,
        }
    form = PayPalPaymentForm(initial=params)
    form.fields['return'] = forms.CharField(max_length=100,
                            widget=forms.HiddenInput,
                            initial=payment.response_page)

    return form


def parse_pdt_validation(data):
    result_params = {}
    success = False
    items_list = data.split('\n')

    for i, item in enumerate(items_list):
        if i == 0:
            success = (item.lower() == 'success')
        else:
            # the item is url encoded - decode it
            result_params.update(cgi.parse_qsl(item))

    return success, result_params


def validate_with_paypal(request, validate_type):
    """
    Validate either PDT or IPN with PayPal.
    """
    if validate_type == 'PDT':
        # we are on return url
        # need to verify if payment is completed
        # MERCHANT_TXN_KEY is your PDT identity token
        params = {
                  'cmd': '_notify-synch',
                  'tx': request.GET.get('tx', ''),
                  'at': settings.MERCHANT_TXN_KEY
                  }
        data = urllib.urlencode(params)

        # Sample response:
        # SUCCESS
        # first_name=Jane+Doe
        # last_name=Smith
        # payment_status=Completed payer_email=janedoesmith%40hotmail.com
        # payment_gross=3.99
        # mc_currency=USD custom=For+the+purchase+of+the+rare+book+Green+Eggs+%26+Ham

        # If the response is FAIL, PayPal recommends making sure that:
        # The Transaction token is not bad.
        # The ID token is not bad.
        # The tokens have not expired.

    else:   # IPN
        data = 'cmd=_notify-validate&%s' % request.POST.urlencode()

        # The response is one single-word: VERIFIED or INVALID

    headers = {"Content-type": "application/x-www-form-urlencoded",
               'encoding': 'utf-8',
               "Accept": "text/plain"}
    request = urllib2.Request(settings.PAYPAL_POST_URL,
                              data,
                              headers)
    response = urllib2.urlopen(request)
    data = response.read()

    if validate_type == 'PDT':
        return parse_pdt_validation(data)
    else:
        return data.strip('\n').lower() == 'verified', None


def verify_no_fraud(response_d, payment):
    # Has duplicate txn_id?
    txn_id = response_d.get('txn_id')
    if not txn_id:
        return False

    txn_id_exists = Payment.objects.filter(trans_id=txn_id).exists()
    if txn_id_exists:
        return False

    # Does receiver_email matches?
    receiver_email = response_d.get('receiver_email')
    if receiver_email != settings.PAYPAL_MERCHANT_LOGIN:
        return False

    # Is the amount correct?
    payment_gross = response_d.get('mc_gross', 0)
    try:
        float(payment_gross)
    except ValueError:
        payment_gross = 0
    if Decimal(payment_gross) != payment.amount:
        return False

    return True


def paypal_thankyou_processing(request, response_d, **kwargs):

    # validate with PayPal
    validate_type = kwargs.get('validate_type', 'PDT')

    if validate_type == 'PDT':
        success, response_d = validate_with_paypal(request, validate_type)
    else:
        success = validate_with_paypal(request, validate_type)[0]
        response_d = dict(map(lambda x: (x[0].lower(), x[1]),
                              response_d.items()))

    if not success:
        raise Http404

    paymentid = response_d.get('invoice', 0)

    try:
        paymentid = int(paymentid)
    except:
        paymentid = 0
    payment = get_object_or_404(Payment, pk=paymentid)
    processed = False

    # To prevent the fraud, verify the following:
    # 1) txn_id is not a duplicate to prevent someone from reusing an old,
    #    completed transaction.
    # 2) receiver_email is an email address registered in your PayPal
    #    account, to prevent the payment from being sent to a fraudulent
    #    account.
    # 3) Other transaction details, such as the item number and price,
    #    to confirm that the price has not been changed.

    # if balance==0, it means already processed
    if payment.invoice.balance > 0:
        # verify before updating database
        is_valid = verify_no_fraud(response_d, payment)

        if is_valid:
            payment_update_paypal(request, response_d, payment)
            payment_processing_object_updates(request, payment)
            processed = True

            # log an event
            log_payment(request, payment)

            # send payment recipients notification
            send_payment_notice(request, payment)

    return payment, processed


def payment_update_paypal(request, response_d, payment, **kwargs):
    payment.first_name = response_d.get('first_name', '')
    payment.last_name = response_d.get('last_name', '')
    address = response_d.get('address1', '')
    if address:
        payment.address = address
    address2 = response_d.get('address2', '')
    if address2:
        payment.address2 = address2
    city = response_d.get('city', '')
    if city:
        payment.city = city
    state = response_d.get('state', '')
    if state:
        payment.state = state
    phone = response_d.get('night_phone_a', '')
    if phone:
        payment.phone = phone

    payment.payment_type = response_d.get('payment_type', '')

    result = response_d.get('payment_status', '')

    if result.lower() == 'completed':
        payment.response_code = '1'
        payment.response_subcode = '1'
        payment.response_reason_code = '1'
        payment.status_detail = 'approved'
        payment.trans_id = response_d.get('txn_id')
        payment.response_reason_text = 'This transaction has been approved.'
    else:
        payment.response_code = 0
        payment.response_reason_code = 0
        payment.response_reason_text = 'This transaction is %s.' % (
                                response_d.get('payment_status')).lower()

    if payment.is_approved:
        payment.mark_as_paid()
        payment.save()
        payment.invoice.make_payment(request.user, payment.amount)
    else:
        if not payment.status_detail:
            payment.status_detail = 'not approved'
        payment.save()

