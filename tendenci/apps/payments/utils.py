import os
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.notifications.utils import send_notifications

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
        from tendenci.apps.site_settings.utils import get_setting

        err_msg = traceback.format_exc()
        subject = 'Payment error from %s (ID:%d)' % (get_setting('site', 'global', 'siteurl'),
                                                     payment.id)
        body = err_msg
        sender = settings.DEFAULT_FROM_EMAIL
        admins = settings.ADMINS
        recipients = [item[1] for item in admins]
        if not recipients:
            recipients = ['programmers@tendenci.com']
        send_mail(subject, body, sender, recipients, fail_silently=True)

        # still want the end user know an error occurred
        raise Exception(err_msg)


def log_silent_post(request, payment):
    # This is redundant to log_payment(), and the Django access log (if enabled
    # in local_settings.py), and the nginx access log (if nginx is used).
    return

    now_str = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    # log the post
    output = """
                %s \n
                Referrer: %s \n
                Content-Type: %s \n
                User-Agent: %s \n\n
                Query-String: \n %s \n
                Remote-Addr: %s \n\n
                Remote-Host: %s \n
                Remote-User: %s \n
                Request-Method: %s \n
            """ % (now_str, request.META.get('HTTP_REFERER', ''),
                   request.META.get('CONTENT_TYPE', ''),
                   request.META.get('HTTP_USER_AGENT', ''),
                   request.META.get('QUERY_STRING', ''),
                   request.META.get('REMOTE_ADDR', ''),
                   request.META.get('REMOTE_HOST', ''),
                   request.META.get('REMOTE_USER', ''),
                   request.META.get('REQUEST_METHOD', ''))

    log_file_name = "silentpost_%d.log" % payment.id
    log_path = os.path.join('silentposts', log_file_name)
    default_storage.save(log_path, ContentFile(output))


def log_payment(request, payment):
    if payment.response_code == '1':
        event_id = 282101
        description = '%s edited - credit card approved ' % payment._meta.object_name
    else:
        event_id = 282102
        description = '%s edited - credit card declined ' % payment._meta.object_name

    log_defaults = {
        'event_id' : event_id,
        'event_data': '%s (%d) edited by %s' % (payment._meta.object_name, payment.pk, request.user),
        'description': description,
        'user': request.user,
        'request': request,
        'instance': payment,
    }
    EventLog.objects.log(**log_defaults)

def send_payment_notice(request, payment):
    notif_context = {
        'request': request,
        'object': payment,
        }

    send_notifications('module','payments', 'paymentrecipients',
            'payment_added', notif_context)
