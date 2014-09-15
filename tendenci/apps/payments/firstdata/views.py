from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.payments.firstdata.utils import firstdata_thankyou_processing
from tendenci.apps.event_logs.models import EventLog
# http://www.firstdata.com/en_us/customer-center/merchants/support/first-data-global-gateway-api-software-landing#/content-product-1
# http://www.firstdata.com/downloads/marketing-merchant/fd_globalgatewayconnect_usermanualnorthamerica.pdf


@csrf_exempt
def thank_you(request, payment_id, template_name='payments/receipt.html'):
    payment = firstdata_thankyou_processing(request, dict(request.POST.items()))

    if payment:
        if payment.is_approved:
            payment.response_reason_text = _("Your transaction has been approved.")
        else:
            payment.response_reason_text = _("Your transaction has been declined.")

    return render_to_response(template_name,{'payment':payment},
                              context_instance=RequestContext(request))
