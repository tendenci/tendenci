
from django.conf import settings
from django.core.urlresolvers import reverse
from django import forms
#from django.http import Http404
from tendenci.core.payments.paypal.forms import PayPalPaymentForm
from tendenci.core.payments.models import Payment
from tendenci.core.payments.utils import payment_processing_object_updates
from tendenci.core.payments.utils import log_payment, send_payment_notice
from tendenci.core.site_settings.utils import get_setting


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
              'address': payment.address,
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


def paypal_thankyou_processing(request, response_d, **kwargs):
    from django.shortcuts import get_object_or_404
    response_d = dict(map(lambda x: (x[0].lower(), x[1]), response_d.items()))

    paymentid = response_d.get('invoice', 0)

    try:
        paymentid = int(paymentid)
    except:
        paymentid = 0
    payment = get_object_or_404(Payment, pk=paymentid)
    processed = False

    if payment.invoice.balance > 0:  # if balance==0, it means already processed
        payment_update_paypal(request, response_d, payment)
        payment_processing_object_updates(request, payment)
        processed = True

        # log an event
        log_payment(request, payment)

        # send payment recipients notification
        send_payment_notice(request, payment)

    return payment, processed


def payment_update_paypal(request, response_d, payment, **kwargs):
    # validate the post data

    payment.first_name = response_d.get('first_name', '')
    payment.last_name = response_d.get('last_name', '')
    payment.address = response_d.get('address', '')
    payment.address2 = response_d.get('address2', '')
    payment.city = response_d.get('city', '')
    payment.state = response_d.get('state', '')
    payment.country = response_d.get('country', '')
    payment.phone = response_d.get('night_phone_a', '')

    result = response_d.get('payment_status', '')
#    respmsg = (response_d.get('respmsg', '')).lower()
#    payment.response_reason_text = respmsg

    if result == 'completed':
        payment.response_code = '1'
        payment.response_subcode = '1'
        payment.response_reason_code = '1'
        payment.status_detail = 'approved'
        payment.trans_id = response_d.get('pnref', '')
    else:
        payment.response_code = 0
        payment.response_reason_code = 0

    if payment.is_approved:
        payment.mark_as_paid()
        payment.save()
        payment.invoice.make_payment(request.user, payment.amount)
    else:
        if not payment.status_detail:
            payment.status_detail = 'not approved'
        payment.save()

