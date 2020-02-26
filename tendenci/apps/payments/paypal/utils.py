from urllib.parse import urlencode
from urllib.request import urlopen, Request
import cgi
from decimal import Decimal

from django.conf import settings
from django.urls import reverse
from django import forms
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db import transaction

from tendenci.apps.payments.paypal.forms import PayPalPaymentForm
from tendenci.apps.payments.models import Payment
from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.payments.utils import log_payment, send_payment_notice
from tendenci.apps.site_settings.utils import get_setting

def prepare_paypal_form(request, payment):
    amount = "%.2f" % payment.amount
    image_url = get_setting('site', 'global', 'merchantlogo')
    site_url = get_setting('site', 'global', 'siteurl')
    notify_url = '%s%s' % (site_url, reverse('paypal.ipn'))
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
        data = urlencode(params)

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
    request = Request(settings.PAYPAL_POST_URL,
                              data.encode('utf-8'),
                              headers)
    response = urlopen(request)
    data = response.read().decode('utf-8')

    if validate_type == 'PDT':
        return parse_pdt_validation(data)
    else:
        return data.strip('\n').lower() == 'verified', None

def verify_no_fraud(response_d, payment):
    # Does receiver_email match?
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

    # Duplicate txn_id?
    txn_id = response_d.get('txn_id')
    if not txn_id:
        return False
    # To prevent a single txn_id from being used for multiple Payments by
    # simultaneously submitting multiple requests using the same txn_id, either
    # the Payment.trans_id column in the database must have a unique constraint,
    # the Payment database table must be locked before checking for duplicates
    # and the lock must be held until after the trans_id has been saved, or
    # trans_id must be updated on the database record for the current Payment
    # object before checking for duplicates.
    #
    # Since the Payment.trans_id column has existed for a long time without a
    # unique constraint, and since it is used by multiple payment modules for
    # independent payment processors that may not all use unique transaction
    # IDs, adding a unique constraint to this column may not be practical.  In
    # addition, since Django does not natively support table locks, and since
    # table locks can lead to performance issues, it is best to avoid table
    # locks.  Therefore this code updates trans_id before checking for
    # duplicates.
    #
    # To ensure that the trans_id update can be seen by other processes before
    # this process checks for duplicates, the database transaction associated
    # with this update must be committed without being nested in any other
    # transactions.  transaction.commit() ensures that this transaction is not
    # nested in any other transactions by committing the current transaction (if
    # autocommit is disabled), by throwing an exception (if called within a
    # transaction.atomic block), or by doing nothing (if this transaction is not
    # nested).  transaction.atomic() with select_for_update() ensures that
    # payment.trans_id cannot be updated in the database by another process
    # after this process calls get_object_or_404() and before this process calls
    # payment.save().
    transaction.commit()
    with transaction.atomic():
        payment = get_object_or_404(Payment.objects.select_for_update(), pk=payment.id)
        if payment.trans_id == '':
            payment.trans_id = txn_id
            payment.save()
        elif payment.trans_id != txn_id:
            return False
    txn_id_exists = Payment.objects.filter(trans_id=txn_id).exclude(pk=payment.id).exists()
    if txn_id_exists:
        with transaction.atomic():
            payment = get_object_or_404(Payment.objects.select_for_update(), pk=payment.id)
            if payment.trans_id == txn_id:
                payment.trans_id = ''
                payment.save()
        return False

    return True

def paypal_thankyou_processing(request, response_d, **kwargs):

    # validate with PayPal
    validate_type = kwargs.get('validate_type', 'PDT')

    if validate_type == 'PDT':
        success, response_d = validate_with_paypal(request, validate_type)
    else:
        success = validate_with_paypal(request, validate_type)[0]
        response_d = dict([(x[0].lower(), x[1]) for x in response_d.items()])

    if not success:
        raise Http404

    paymentid = response_d.get('invoice', 0)

    try:
        paymentid = int(paymentid)
    except:
        paymentid = 0
    payment = get_object_or_404(Payment, pk=paymentid)
    processed = False

    if payment.is_approved:  # if already processed
        return payment, processed

    # To prevent fraud, verify the following before updating the database:
    # 1) txn_id is not a duplicate to prevent someone from reusing an old,
    #    completed transaction.
    # 2) receiver_email is an email address registered in your PayPal
    #    account, to prevent the payment from being sent to a fraudulent
    #    account.
    # 3) Other transaction details, such as the item number and price,
    #    to confirm that the price has not been changed.
    if not verify_no_fraud(response_d, payment):
        return payment, processed

    with transaction.atomic():
        # verify_no_fraud() cannot be run within a transaction, so we must
        # re-retrieve payment and re-check payment.is_approved within a
        # transaction after calling verify_no_fraud() in order to prevent
        # duplicate processing of simultaneous redundant payment requests
        payment = get_object_or_404(Payment.objects.select_for_update(), pk=paymentid)
        if not payment.is_approved:  # if not already processed
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
