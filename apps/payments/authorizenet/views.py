from django.shortcuts import render_to_response
from django.template import RequestContext
from payments.authorizenet.utils import authorizenet_thankyou_processing
from event_logs.models import EventLog

def sim_thank_you(request, payment_id, template_name='payments/authorizenet/thankyou.html'):
    payment = authorizenet_thankyou_processing(request.user, dict(request.POST.items()))
    
    # log an event for payment edit
    if payment:
        if payment.response_code == '1':
            event_id = 282101
            description = '%s edited - credit card approved ' % payment._meta.object_name
        else:
            event_id = 282102
            description = '%s edited - credit card declined ' % payment._meta.object_name
            
        log_defaults = {
            'event_id' : event_id,
            'event_data': '%s (%d) edited by %s' % (payment._meta.object_name, payment.pk, request.user),
            'description': description,
            'user': request.user,
            'request': request,
            'instance': payment,
        }
        EventLog.objects.log(**log_defaults)
    
    return render_to_response(template_name,{'payment':payment}, 
                              context_instance=RequestContext(request))