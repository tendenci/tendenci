import os
from datetime import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from payments.models import Payment
from forms import StripeCardForm, BillingInfoForm
import stripe


@csrf_exempt
def pay_online(request, payment_id, template_name='payments/stripe/payonline.html'):
    payment = get_object_or_404(Payment, pk=payment_id) 
    form = StripeCardForm(request.POST or None)
    billing_info_form = BillingInfoForm(request.POST or None, instance=payment)
    if request.method == "POST":
        if form.is_valid():
            # get stripe token and make a payment immediately
            stripe.api_key = settings.get('STRIPE_SECRET_KEY', '')
            token = request.POST.get('stripe_token')
            
            # create the charge on Stripe's servers - this will charge the user's card
            charge = stripe.Charge.create(
                amount=payment.amount, # amount in cents, again
                currency="usd",
                card=token,
                description=payment.description
            )
            
            if billing_info_form.is_valid():
                payment = billing_info_form.save()
                
            # update payment status and object
            
            # redirect to thankyou
            return HttpResponseRedirect(reverse('stripe.thank_you'))
        
    return render_to_response(template_name, {'form': form, 
                                              'billing_info_form': billing_info_form},
                              context_instance=RequestContext(request))

@csrf_exempt
def thank_you(request, payment_id, template_name='payments/receipt.html'):
    #payment, processed = stripe_thankyou_processing(request, dict(request.POST.items()))
    payment = get_object_or_404(Payment, pk=payment_id) 

    return render_to_response(template_name,{'payment':payment}, 
                              context_instance=RequestContext(request))