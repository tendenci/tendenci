from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from payments.firstdata.utils import firstdata_thankyou_processing
from event_logs.models import EventLog
# http://www.firstdata.com/en_us/customer-center/merchants/support/first-data-global-gateway-api-software-landing#/content-product-1
# http://www.firstdata.com/downloads/marketing-merchant/fd_globalgatewayconnect_usermanualnorthamerica.pdf


@csrf_exempt
def thank_you(request, payment_id, template_name='payments/receipt.html'):
    payment = firstdata_thankyou_processing(request, dict(request.POST.items()))

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

    if payment:
        if payment.is_approved:
            payment.response_reason_text = "Your transaction has been approved."
        else:
            payment.response_reason_text = "Your transaction has been declined."

    return render_to_response(template_name,{'payment':payment}, 
                              context_instance=RequestContext(request))
