from __future__ import absolute_import
#import os
import math
import traceback
#from datetime import datetime
from django.shortcuts import render_to_response, get_object_or_404
#from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

import simplejson

from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.payments.utils import log_payment, send_payment_notice
from tendenci.apps.payments.models import Payment
from .forms import StripeCardForm, BillingInfoForm
import stripe
from .utils import payment_update_stripe
from tendenci.apps.site_settings.utils import get_setting


@csrf_exempt
def pay_online(request, payment_id, template_name='payments/stripe/payonline.html'):
    payment = get_object_or_404(Payment, pk=payment_id)
    form = StripeCardForm(request.POST or None)
    billing_info_form = BillingInfoForm(request.POST or None, instance=payment)
    currency = get_setting('site', 'global', 'currency')
    if not currency:
        currency = 'usd'
    if request.method == "POST":
        if form.is_valid():
            # get stripe token and make a payment immediately
            stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            token = request.POST.get('stripe_token')

            if billing_info_form.is_valid():
                payment = billing_info_form.save()

            # create the charge on Stripe's servers - this will charge the user's card
            params = {
                       'amount': math.trunc(payment.amount * 100), # amount in cents, again
                       'currency': currency,
                       'card': token,
                       'description': payment.description
                      }

            try:
                charge_response = stripe.Charge.create(**params)
                # an example of response: https://api.stripe.com/v1/charges/ch_YjKFjLIItzRDv7
                #charge_response = simplejson.loads(charge)
            except Exception as e:
                charge_response = e.message
            
            # update payment status and object
            if  payment.invoice.balance > 0:
                payment_update_stripe(request, charge_response, payment)
                payment_processing_object_updates(request, payment)

                # log an event
                log_payment(request, payment)

                # send payment recipients notification
                send_payment_notice(request, payment)

            # redirect to thankyou
            return HttpResponseRedirect(reverse('stripe.thank_you', args=[payment.id]))

    return render_to_response(template_name, {'form': form,
                                              'billing_info_form': billing_info_form,
                                              'payment': payment},
                              context_instance=RequestContext(request))

@csrf_exempt
def thank_you(request, payment_id, template_name='payments/receipt.html'):
    #payment, processed = stripe_thankyou_processing(request, dict(request.POST.items()))
    payment = get_object_or_404(Payment, pk=payment_id)

    return render_to_response(template_name,{'payment':payment},
                              context_instance=RequestContext(request))
