
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
        
        