from datetime import timedelta
from perms.utils import is_admin
from perms.utils import get_notice_recipients
try:
    from notification import models as notification
except:
    notification = None

# update the object
def payment_processing_object_updates(request, payment, **kwargs):
    # process based on invoice object type - needs lots of work here.
    if str(payment.response_code) == '1' and str(payment.response_reason_code) == '1':
        if payment.invoice.invoice_object_type == 'job':
            from jobs.models import Job
            try:
                job = Job.objects.get(id=payment.invoice.invoice_object_type_id)
                if not is_admin(request.user):
                    job.status_detail = 'paid - pending approval'
                job.expiration_dt = job.activation_dt + timedelta(days=job.requested_duration)
                job.save()
            except Job.DoesNotExist:
                pass
            
        if payment.invoice.invoice_object_type == 'directory':
            from directories.models import Directory
            try:
                directory = Directory.objects.get(id=payment.invoice.invoice_object_type_id)
                if not is_admin(request.user):
                    directory.status_detail = 'paid - pending approval'
                directory.expiration_dt = directory.activation_dt + timedelta(days=directory.requested_duration)
                directory.save()
            except Directory.DoesNotExist:
                pass
            
        if payment.invoice.invoice_object_type == 'donation':
            from donations.models import Donation
            
            # send admin an email when donation has been paid
            try:
                donation = Donation.objects.get(id=payment.invoice.invoice_object_type_id)
                invoice = donation.invoice
                # email to admin (if payment type is credit card email is not sent until payment confirmed)
                recipients = get_notice_recipients('module', 'donations', 'donationsrecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'donation': donation,
                            'invoice': invoice,
                            'request': request,
                        }
                        notification.send_emails(recipients,'donation_added', extra_context)
            except Donation.DoesNotExist:
                pass
            
