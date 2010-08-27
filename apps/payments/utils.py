from datetime import timedelta
from perms.utils import is_admin


# update the object
def payment_processing_object_updates(user, payment, **kwargs):
    # process based on invoice object type - needs lots of work here.
    if str(payment.response_code) == '1' and str(payment.response_reason_code) == '1':
        if payment.invoice.invoice_object_type == 'job':
            from jobs.models import Job
            try:
                job = Job.objects.get(id=payment.invoice.invoice_object_type_id)
                if not is_admin(user):
                    job.status_detail = 'paid - pending approval'
                job.expiration_dt = job.activation_dt + timedelta(days=job.requested_duration)
                job.save()
            except Job.DoesNotExist:
                pass
            
        if payment.invoice.invoice_object_type == 'directory':
            from directories.models import Directory
            try:
                directory = Directory.objects.get(id=payment.invoice.invoice_object_type_id)
                if not is_admin(user):
                    directory.status_detail = 'paid - pending approval'
                directory.expiration_dt = directory.activation_dt + timedelta(days=directory.requested_duration)
                directory.save()
            except Directory.DoesNotExist:
                pass
