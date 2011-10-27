import os
from datetime import datetime
from django.conf import settings

# update the object
def payment_processing_object_updates(request, payment, **kwargs):
    # they are paid, so update the object
    # trap the error and send us the error email - just in case
    try:
        if str(payment.response_code) == '1' and str(payment.response_reason_code) == '1':
            obj = payment.invoice.get_object()
            if obj and hasattr(obj, 'auto_update_paid_object'):
                obj.auto_update_paid_object(request, payment)
    except:
        import traceback
        from django.core.mail import send_mail
        from django.conf import settings
        from site_settings.utils import get_setting
        
        err_msg = traceback.format_exc()
        subject = 'Payment error from %s (ID:%d)' % (get_setting('site', 'global', 'siteurl'), 
                                                     payment.id)
        body = err_msg
        sender = settings.DEFAULT_FROM_EMAIL
        admins = settings.ADMINS
        recipients = [item[1] for item in admins]
        if not recipients:
            recipients = ['jqian@schipul.com']
        send_mail(subject, body, sender, recipients, fail_silently=True)
        
        # still want the end user know an error occurred
        raise Exception, err_msg
    
    
def log_silent_post(request, payment):    
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
        
        