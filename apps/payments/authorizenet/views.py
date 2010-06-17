from django.shortcuts import render_to_response
from django.template import RequestContext
from payments.models import Payment
from payments.authorizenet.signals import payment_was_successful, payment_was_flagged

def sim_thank_you(request, payment_id, template_name='payments/authorizenet/thankyou.html'):
    payment = Payment.objects.create_from_dict(request.POST)
    if payment.is_approved:
        payment_was_successful.send(sender=payment)
    else:
        payment_was_flagged.send(sender=payment)
    return render_to_response(template_name, context_instance=RequestContext(request))