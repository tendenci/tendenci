from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from tendenci.core.payments.authorizenet.utils import authorizenet_thankyou_processing
from tendenci.core.payments.utils import log_silent_post


@csrf_exempt
def sim_thank_you(request, payment_id,
                  template_name='payments/authorizenet/thankyou.html'):
    payment = authorizenet_thankyou_processing(
                                        request,
                                        dict(request.POST.items()))

    return render_to_response(template_name, {'payment': payment},
                              context_instance=RequestContext(request))


@csrf_exempt
def silent_post(request):
    # for now, we only handle AUTH_CAPTURE AND AUTH_ONLY
    if not request.POST.get('x_type', '').lower() in ['auth_capture', 'auth_only']:
        return HttpResponse('')

    payment = authorizenet_thankyou_processing(
        request, dict(request.POST.items()))

    log_silent_post(request, payment)

    return HttpResponse('ok')
