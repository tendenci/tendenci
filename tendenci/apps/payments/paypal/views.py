from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from tendenci.apps.payments.paypal.utils import paypal_thankyou_processing
from tendenci.apps.payments.utils import log_silent_post


@csrf_exempt
def thank_you(request, template_name='payments/receipt.html'):
    validate_type = 'PDT'
    payment, processed = paypal_thankyou_processing(request,
                                    dict(request.POST.items()),
                                    validate_type=validate_type)

    return render_to_response(template_name, {'payment': payment},
                              context_instance=RequestContext(request))


@csrf_exempt
def ipn(request):
    validate_type = 'IPN'
    payment, processed = paypal_thankyou_processing(request,
                                dict(request.POST.items()),
                                validate_type=validate_type)

    if processed:
        log_silent_post(request, payment)

    return HttpResponse('ok')
