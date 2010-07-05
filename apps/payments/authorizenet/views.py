from django.shortcuts import render_to_response
from django.template import RequestContext
from payments.authorizenet.utils import authorizenet_thankyou_processing

def sim_thank_you(request, payment_id, template_name='payments/authorizenet/thankyou.html'):
    payment = authorizenet_thankyou_processing(request.user, dict(request.POST.items()))
    
    return render_to_response(template_name,{'payment':payment}, 
                              context_instance=RequestContext(request))