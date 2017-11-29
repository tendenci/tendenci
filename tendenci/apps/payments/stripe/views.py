#import os
import math
#from datetime import datetime
from django.shortcuts import render_to_response, get_object_or_404
#from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
# import simplejson

from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.payments.utils import log_payment, send_payment_notice
from tendenci.apps.payments.models import Payment
from forms import StripeCardForm, BillingInfoForm
import stripe
from utils import payment_update_stripe
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.recurring_payments.models import RecurringPayment
from tendenci.apps.base.http import Http403
from tendenci.apps.perms.utils import has_perm


def pay_online(request, payment_id, template_name='payments/stripe/payonline.html'):
    with transaction.atomic():
        payment = get_object_or_404(Payment.objects.select_for_update(), pk=payment_id)
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
                try:
                    # Create a Customer:
                    customer = stripe.Customer.create(
                                email=obj_user.email,
                                description="For membership auto renew",
                                source=token,
                    )
                except:
                    customer = None

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
            except stripe.error.CardError as e:
                # it's a decline
                json_body = e.json_body
                err  = json_body and json_body['error']
                code = err and err['code']
                message = err and err['message']
                charge_response = '{message} status={status}, code={code}'.format(
                            message=message, status=e.http_status, code=code)
            except Exception as e:
                charge_response = e.message
               
            # add a rp entry now 
            if hasattr(charge_response,'paid') and charge_response.paid:
                if customer and membership:
                    kwargs = {'platform': 'stripe',
                              'customer_profile_id': customer.id,
                              }
                    membership.get_or_create_rp(request.user, **kwargs)

            # update payment status and object
            if not payment.is_approved:  # if not already processed
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


@login_required
def update_card(request, rp_id):
    rp = get_object_or_404(RecurringPayment, pk=rp_id, platform='stripe')
    if not has_perm(request.user, 'recurring_payments.change_recurringpayment', rp) \
        and not (rp.owner is request.user):
        raise Http403
    
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    token = request.POST.get('stripeToken')
    try:
        if not rp.customer_profile_id:
            customer = stripe.Customer.create(
                            email=rp.user.email,
                            description=rp.description,
                            source=token)
            rp.customer_profile_id = customer.id
            rp.save()
            msg_string = 'Successfully added payment method'
        else:
            customer = stripe.Customer.retrieve(rp.customer_profile_id)
            customer.source = token
            customer.save()
            msg_string = 'Successfully updated payment method'
        message_status = messages.SUCCESS
    except stripe.error.CardError as e:
        # it's a decline
        json_body = e.json_body
        err  = json_body and json_body['error']
        code = err and err['code']
        message = err and err['message']
        message_status = messages.ERROR
        msg_string = '{message} status={status}, code={code}'.format(
                            message=message, status=e.http_status, code=code)
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        message_status = messages.ERROR
        msg_string = 'Error updating payment method: {}'.format(e)
    
    messages.add_message(request, message_status, _(msg_string))
    next_page = request.GET.get('next')
    if next_page:
        return HttpResponseRedirect(next_page)
    else:
        return HttpResponseRedirect(reverse('recurring_payment.view_account', args=[rp.id]))
    

def thank_you(request, payment_id, template_name='payments/receipt.html'):
    #payment, processed = stripe_thankyou_processing(request, dict(request.POST.items()))
    payment = get_object_or_404(Payment, pk=payment_id)

    return render_to_response(template_name,{'payment':payment},
                              context_instance=RequestContext(request))
