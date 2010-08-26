# settings - directoriespaymenttypes, directoriesrequirespayment
from directories.models import DirectoryPricing
from invoices.models import Invoice
from payments.models import Payment
from perms.utils import is_admin
from site_settings.utils import get_setting

def get_duration_choices():
    dps = DirectoryPricing.objects.filter(status=1).order_by('duration')
    
    return [(dp.duration, '%d days after the activation date' % dp.duration) for dp in dps]

def get_payment_method_choices(user):
    if is_admin(user):
        return (('paid - check', 'User paid by check'),
                ('paid - cc', 'User paid by credit card'),
                ('Credit Card', 'Make online payment NOW'),)
    else:
        directory_payment_types = get_setting('module', 'directories', 'directoriespaymenttypes')
        if directory_payment_types:
            directory_payment_types_list = directory_payment_types.split(',')
            directory_payment_types_list = [item.strip() for item in directory_payment_types_list]
            
            return [(item, item) for item in directory_payment_types_list]
        else:
            return ()
  
def directory_set_inv_payment(user, directory, **kwargs): 
    if get_setting('module', 'directories', 'directoriesrequirespayment'):
        if not directory.invoice:
            inv = Invoice()
            inv.invoice_object_type = "directory"
            inv.invoice_object_type_id = directory.id
            inv.assign_directory_info(user, directory)
            inv.total = get_directory_price(user, directory)
            inv.subtotal = inv.total
            inv.balance = inv.total
            inv.estimate = 1
            inv.status_detail = 'estimate'
            inv.save(user)
            
            # update job
            directory.invoice = inv
            directory.save()
            
            if is_admin(user):
                if directory.payment_method in ['paid - cc', 'paid - check', 'paid - wire transfer']:
                    boo_inv = inv.tender(user) 
                    
                    # payment
                    payment = Payment()
                    boo = payment.payments_pop_by_invoice_user(user, inv, inv.guid)
                    payment.mark_as_paid()
                    payment.method = directory.payment_method
                    payment.save(user)
                    
                    # this will make accounting entry
                    inv.make_payment(user, payment.amount)
                    
            
def get_directory_price(user, directory, **kwargs):
    directory_price = 0
    dps = DirectoryPricing.objects.filter(status=1).filter(duration=directory.requested_duration)
    if dps:
        dp = dps[0]
        # check if user is member when membership is in place
        if directory.list_type == 'regular':
            directory_price = dp.regular_price
        else:
            directory_price = dp.premium_price
            
    return directory_price
    