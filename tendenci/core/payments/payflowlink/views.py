import os
from datetime import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from tendenci.core.payments.payflowlink.utils import payflowlink_thankyou_processing
from tendenci.core.payments.utils import log_silent_post

@csrf_exempt
def thank_you(request, template_name='payments/receipt.html'):
    payment, processed = payflowlink_thankyou_processing(request, dict(request.POST.items()))

    return render_to_response(template_name,{'payment':payment},
                              context_instance=RequestContext(request))

@csrf_exempt
def silent_post(request):
    payment, processed = payflowlink_thankyou_processing(request, dict(request.POST.items()))

    if processed:
        log_silent_post(request, payment)

    return HttpResponse('ok')
