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
from forms import StripeCardForm, BillingInfoForm
import stripe
from utils import payment_update_stripe
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.recurring_payments.models import RecurringPayment


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
                
            # determine if we need to create a stripe customer (for membership auto renew)
            customer = False
            obj_user = None
            membership = None
            obj = payment.invoice.get_object()
            if obj and hasattr(obj, 'memberships'):
                membership = obj.memberships()[0]
                if membership.auto_renew and not membership.has_rp(platform='stripe'):
                    obj_user = membership.user
                else:
                    membership = None
                    
            if obj_user:
                # Create a Customer:
                customer = stripe.Customer.create(
                            email=obj_user.email,
                            description="For membership auto renew",
                            source=token,
                )

            # create the charge on Stripe's servers - this will charge the user's card
            params = {
                       'amount': math.trunc(payment.amount * 100), # amount in cents, again
                       'currency': currency,
                       'description': payment.description
                      }
            if customer:
                params.update({'customer': customer.id})
            else:
                params.update({'card': token})

            try:
                charge_response = stripe.Charge.create(**params)
                # an example of response: https://api.stripe.com/v1/charges/ch_YjKFjLIItzRDv7
                #charge_response = simplejson.loads(charge)
            except Exception, e:
                charge_response = e.message
               
            # add a rp entry now 
            if hasattr(charge_response,'paid') and charge_response.paid:
                if customer and membership:
                    kwargs = {'platform': 'stripe',
                              'customer_profile_id': customer.id,
                              }
                    membership.get_or_create_rp(request.user, **kwargs)
                    
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
                                              'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
                                              'payment': payment},
                              context_instance=RequestContext(request))

@csrf_exempt
def thank_you(request, payment_id, template_name='payments/receipt.html'):
    #payment, processed = stripe_thankyou_processing(request, dict(request.POST.items()))
    payment = get_object_or_404(Payment, pk=payment_id)

    return render_to_response(template_name,{'payment':payment},
                              context_instance=RequestContext(request))
