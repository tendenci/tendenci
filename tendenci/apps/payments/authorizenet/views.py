from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.payments.authorizenet.utils import authorizenet_thankyou_processing
from tendenci.apps.payments.utils import log_silent_post


@csrf_exempt
def sim_thank_you(request, payment_id,
                  template_name='payments/authorizenet/thankyou.html'):
    payment = authorizenet_thankyou_processing(
                                        request,
                                        request.POST.copy())

    return render_to_resp(request=request, template_name=template_name,
                              context={'payment': payment})


@csrf_exempt
def silent_post(request):
    # for now, we only handle AUTH_CAPTURE AND AUTH_ONLY
    if not request.POST.get('x_type', '').lower() in ['auth_capture', 'auth_only']:
        return HttpResponse('')

    payment = authorizenet_thankyou_processing(
        request, request.POST.copy())

    log_silent_post(request, payment)

    return HttpResponse('ok')
