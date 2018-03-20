from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.firstdatae4.utils import firstdatae4_thankyou_processing
from tendenci.apps.payments.utils import log_silent_post


@csrf_exempt
def thank_you(request,
                  template_name='payments/authorizenet/thankyou.html'):
    payment = firstdatae4_thankyou_processing(
                                        request,
                                        request.POST.copy())
    if not payment:
        return HttpResponse('Not Valid')

    return render_to_resp(request=request, template_name=template_name,
                              context={'payment': payment})


@csrf_exempt
def silent_post(request):
    payment = firstdatae4_thankyou_processing(
        request, request.POST.copy())

    if not payment:
        return HttpResponse('Not Valid')

    log_silent_post(request, payment)

    return HttpResponse('ok')
