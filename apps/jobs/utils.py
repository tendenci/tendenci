# settings - jobspaymenttypes, jobsrequirespayment
from jobs.models import JobPricing
from invoices.models import Invoice
from payments.models import Payment
from perms.utils import is_admin
from site_settings.utils import get_setting

def get_duration_choices():
    jps = JobPricing.objects.filter(status=1).order_by('duration')
    
    return [(jp.duration, '%d days after the activation date' % jp.duration) for jp in jps]

def get_payment_method_choices(user):
    if is_admin(user):
        return (('paid - check', 'User paid by check'),
                ('paid - cc', 'User paid by credit card'),
                ('Credit Card', 'Make online payment NOW'),)
    else:
        job_payment_types = get_setting('module', 'jobs', 'jobspaymenttypes')
        if job_payment_types:
            job_payment_types_list = job_payment_types.split(',')
            job_payment_types_list = [item.strip() for item in job_payment_types_list]
            
            return [(item, item) for item in job_payment_types_list]
        else:
            return ()
  
def job_set_inv_payment(user, job, **kwargs): 
    if get_setting('module', 'jobs', 'jobsrequirespayment'):
        if not job.invoice:
            inv = Invoice()
            inv.invoice_object_type = "job"
            inv.invoice_object_type_id = job.id
            inv.assign_job_info(user, job)
            inv.total = get_job_price(user, job)
            inv.subtotal = inv.total
            inv.balance = inv.total
            inv.estimate = 1
            inv.status_detail = 'estimate'
            inv.save(user)
            
            # update job
            job.invoice = inv
            job.save()
            
            if is_admin(user):
                if job.payment_method in ['paid - cc', 'paid - check', 'paid - wire transfer']:
                    boo_inv = inv.tender(user) 
                    
                    # payment
                    payment = Payment()
                    boo = payment.payments_pop_by_invoice_user(user, inv, inv.guid)
                    payment.mark_as_paid()
                    payment.method = job.payment_method
                    payment.save(user)
                    
                    # this will make accounting entry
                    inv.make_payment(user, payment.amount)
                    
            
def get_job_price(user, job, **kwargs):
    job_price = 0
    jps = JobPricing.objects.filter(status=1).filter(duration=job.requested_duration)
    if jps:
        jp = jps[0]
        # check if user is member when membership is in place
        if job.list_type == 'regular':
            job_price = jp.regular_price
        else:
            job_price = jp.premium_price
            
        job.non_member_price = job_price
        job.non_member_count = 1
            
    return job_price
    