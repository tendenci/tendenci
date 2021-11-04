#import os
import math
import json
import uuid
#from datetime import datetime

from django.shortcuts import get_object_or_404
#from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View
from django.shortcuts import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.middleware.csrf import _compare_salted_tokens
import requests
from square.client import Client

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.payments.utils import log_payment, send_payment_notice
from tendenci.apps.payments.models import Payment
from .forms import SquareCardForm, BillingInfoForm
from .utils import payment_update_square
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.recurring_payments.models import RecurringPayment
from tendenci.apps.base.http import Http403
from tendenci.apps.perms.utils import has_perm

def pay_online(request, payment_id, guid='', template_name='payments/square/payonline.html'):
    if not getattr(settings, 'SQUARE_ACCESS_TOKEN', ''):
        url_setup_guide = 'https://www.tendenci.com/help-files/setting-up-online-payment-processor-and-merchant-provider-on-a-tendenci-site/'
        url_setup_guide = '<a href="{0}">{0}</a>'.format(url_setup_guide)
        merchant_provider = get_setting("site", "global", "merchantaccount")
        msg_string = str(_('ERROR: Online payment has not yet be set up or configured correctly. '))
        if request.user.is_superuser:
            msg_string += str(_('Please follow the guide {0} to complete the setup process for {1}, then try again.').format(url_setup_guide, merchant_provider))
        else:
            msg_string += str(_('Please contact the site administrator to complete the setup process.'))
            
        messages.add_message(request, messages.ERROR, _(msg_string))
        
        payment = get_object_or_404(Payment, pk=payment_id, guid=guid)
    
        return HttpResponseRedirect(reverse('invoice.view', args=[payment.invoice.id]))

    if settings.SQUARE_ENVIRONMENT == 'sandbox':
        payment_form_url = "https://sandbox.web.squarecdn.com/v1/square.js"
    else:
        payment_form_url = "https://web.squarecdn.com/v1/square.js"
            
    with transaction.atomic():
        payment = get_object_or_404(Payment.objects.select_for_update(), pk=payment_id, guid=guid)
        form = SquareCardForm(request.POST or None)
        billing_info_form = BillingInfoForm(request.POST or None, instance=payment)
        currency = get_setting('site', 'global', 'currency')
        if not currency:
            currency = 'usd'
        if request.method == "POST" and form.is_valid():
            # get square token and make a payment immediately
            api_key = getattr(settings, 'SQUARE_ACCESS_TOKEN', '')
            token = request.POST.get('square_token')
            client = Client(
                access_token=api_key,
                environment= settings.SQUARE_ENVIRONMENT,
            )

            if billing_info_form.is_valid():
                payment = billing_info_form.save()

            # determine if we need to create a square customer (for membership auto renew)
            customer = False
            obj_user = None
            membership = None
            obj = payment.invoice.get_object()
            if obj and hasattr(obj, 'memberships'):
                if obj.memberships:
                    membership = obj.memberships()[0]
                    if membership.auto_renew and not membership.has_rp(platform='square'):
                        obj_user = membership.user
                    else:
                        membership = None

            if obj_user:
                try:
                    # Create a Customer:
                    customer = client.customer.create_customer(
                         body={                           
                            "idempotency_key": str(uuid.uuid4()),
                            "email_address": obj_user.email,
                            "note": "For membership auto renew",                            
                        }                                
                    )
                except:
                    customer = None

            # https://github.com/square/square-python-sdk/blob/master/doc/models/create-customer-response.md

            # create the charge on Square's servers - this will charge the user's card
            params = {
                       "source_id": token,
                        "idempotency_key": str(uuid.uuid4()),
                        "amount_money": {
                            "amount": math.trunc(payment.amount * 100), # amount in cents, again
                            "currency": currency,
                        },
                       'note': payment.description
                      }
            if customer:
                params.update({'customer_id': customer.id})

            
            charge_response = client.payments.create_payment(body=params)
                # an example of response: https://github.com/square/square-python-sdk/blob/master/doc/models/create-payment-response.md
            if charge_response.is_error():
                # it's a decline
                charge_response = '{cat} error={message}, code={code}'.format(
                            message=charge_response.detail, cat=charge_response.category, code=charge_response.code)

            # add a rp entry now
            if hasattr(charge_response,'status') and charge_response.status == "COMPLETED":
                if customer and membership:
                    kwargs = {'platform': 'square',
                              'customer_profile_id': customer.id,
                              'token': token,
                              }
                    membership.get_or_create_rp(request.user, **kwargs)

            # update payment status and object
            if not payment.is_approved:  # if not already processed
                payment_update_square(request, charge_response, payment)
                payment_processing_object_updates(request, payment)

                # log an event
                log_payment(request, payment)

                # send payment recipients notification
                send_payment_notice(request, payment)

            # redirect to thankyou
            return HttpResponseRedirect(reverse('square.thank_you', args=[payment.id, payment.guid]))

    return render_to_resp(request=request, template_name=template_name,
                              context={'form': form,
                                              'billing_info_form': billing_info_form,
                                              'payment_form_url': payment_form_url,
                                              'SQUARE_APPLICATION_ID': settings.SQUARE_APPLICATION_ID,
                                              'SQUARE_LOCATION_ID': settings.SQUARE_LOCATION_ID,
                                              'payment': payment})

# this needs fully built out before it can be live
@login_required
def update_card(request, rp_id):
    rp = get_object_or_404(RecurringPayment, pk=rp_id, platform='square')
    if not has_perm(request.user, 'recurring_payments.change_recurringpayment', rp) \
        and not (rp.user and rp.user.id == request.user.id):
        raise Http403

    api_key = getattr(settings, 'SQUARE_ACCESS_TOKEN', '')
    token = request.POST.get('square_token')
    client = Client(
        access_token=api_key,
        environment= settings.SQUARE_ENVIRONMENT,
    )

    if not rp.customer_profile_id:
        customer = client.customer.create_customer(
                body={                           
                "idempotency_key": str(uuid.uuid4()),
                "email_address": rp.user.email,
                "note": rp.description,                    
            }                             
        )
        rp.customer_profile_id = customer.id
        rp.save()
    else:
        customer = client.customer.retrieve_customer(rp.customer_profile_id)

    #square has a many to one relationship with CC cards to customer
    #we can allow just one to keep things simple for now

    # try:
    #     client.cards.create_card(body={
    #         "idempotency_key": str(uuid.uuid4()),
    #         "source_id": token,
    #         "card": {
    #             "customer_id": customer.id,
    #         }
    #     })
            
    # except square.error.CardError as e:
    #     # it's a decline
    #     json_body = e.json_body
    #     err  = json_body and json_body['error']
    #     code = err and err['code']
    #     message = err and err['message']
    #     message_status = messages.ERROR
    #     msg_string = '{message} status={status}, code={code}'.format(
    #                         message=message, status=e.http_status, code=code)
    # except Exception as e:
    #     # Something else happened, completely unrelated to Square
    #     message_status = messages.ERROR
    #     msg_string = 'Error updating payment method: {}'.format(e)

    # messages.add_message(request, message_status, _(msg_string))
    next_page = request.GET.get('next')
    if next_page:
        return HttpResponseRedirect(next_page)
    else:
        return HttpResponseRedirect(reverse('recurring_payment.view_account', args=[rp.id]))


def thank_you(request, payment_id, guid='', template_name='payments/receipt.html'):
    #payment, processed = square_thankyou_processing(request, dict(request.POST.items()))
    payment = get_object_or_404(Payment, pk=payment_id, guid=guid)

    return render_to_resp(request=request, template_name=template_name,
                              context={'payment':payment})
