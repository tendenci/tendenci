from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.paypal.utils import paypal_thankyou_processing
from tendenci.apps.payments.utils import log_silent_post


@csrf_exempt
def thank_you(request, template_name='payments/receipt.html'):
    validate_type = 'PDT'
    payment, processed = paypal_thankyou_processing(request,
                                    request.POST.copy(),
                                    validate_type=validate_type)

    return render_to_resp(request=request, template_name=template_name,
                              context={'payment': payment})


@csrf_exempt
def ipn(request):
    validate_type = 'IPN'
    payment, processed = paypal_thankyou_processing(request,
                                request.POST.copy(),
                                validate_type=validate_type)

    if processed:
        log_silent_post(request, payment)

    return HttpResponse('ok')
