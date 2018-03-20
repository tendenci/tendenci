from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.firstdata.utils import firstdata_thankyou_processing
# http://www.firstdata.com/en_us/customer-center/merchants/support/first-data-global-gateway-api-software-landing#/content-product-1
# http://www.firstdata.com/downloads/marketing-merchant/fd_globalgatewayconnect_usermanualnorthamerica.pdf


@csrf_exempt
def thank_you(request, payment_id, template_name='payments/receipt.html'):
    payment = firstdata_thankyou_processing(request, request.POST.copy())

    if payment:
        if payment.is_approved:
            payment.response_reason_text = _("Your transaction has been approved.")
        else:
            payment.response_reason_text = _("Your transaction has been declined.")

    return render_to_resp(request=request, template_name=template_name,
                              context={'payment':payment})
