import os
from datetime import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from payments.authorizenet.utils import authorizenet_thankyou_processing


@csrf_exempt
def sim_thank_you(request, payment_id, template_name='payments/authorizenet/thankyou.html'):
    payment = authorizenet_thankyou_processing(request, dict(request.POST.items()))
    
    return render_to_response(template_name,{'payment':payment}, 
                              context_instance=RequestContext(request))

   
@csrf_exempt
def silent_post(request):
    payment = authorizenet_thankyou_processing(request, dict(request.POST.items()))
    
    now_str = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    # log the post
    output = """
                %s \n
                Referrer: %s \n
                Remote Address: %s \n
                Content-Type: %s \n
                User-Agent: %s \n\n
                Query-String: \n %s \n
                Remote-Addr: %s \n\n
                Remote-Host: %s \n
                Remote-User: %s \n
                Request-Method: %s \n
            """ % (now_str, request.META.get('HTTP_REFERER', ''),
                   request.META.get('REMOTE_ADDR', ''),
                   request.META.get('CONTENT_TYPE', ''),
                   request.META.get('HTTP_USER_AGENT', ''),
                   request.META.get('QUERY_STRING', ''),
                   request.META.get('REMOTE_ADDR', ''),
                   request.META.get('REMOTE_HOST', ''),
                   request.META.get('REMOTE_USER', ''),
                   request.META.get('REQUEST_METHOD', ''))
            
    log_file_name = "silentpost_%d.log" % payment.id
    log_path = os.path.join(settings.MEDIA_ROOT, 'silentposts/')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    log_path = os.path.join(log_path, log_file_name)
    
    fd = open(log_path, 'w')
    fd.write(output)
    fd.close()
    
    return HttpResponse('ok')
