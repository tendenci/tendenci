from django.shortcuts import render_to_response
from django.template import RequestContext
from payments.authorizenet.utils import authorizenet_thankyou_processing
from payments.utils import payment_processing_thankyou_display

def sim_thank_you(request, payment_id, template_name='payments/authorizenet/thankyou.html'):
    payment = authorizenet_thankyou_processing(request.user, dict(request.POST.items()))
    html_display = payment_processing_thankyou_display(payment)
    
    return render_to_response(template_name,{'html_display':html_display}, 
                              context_instance=RequestContext(request))