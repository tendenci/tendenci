# settings - directoriespaymenttypes, directoriesrequirespayment
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from directories.models import DirectoryPricing
from invoices.models import Invoice
from payments.models import Payment
from perms.utils import is_admin, is_member
from site_settings.utils import get_setting

def get_duration_choices(user):
    currency_symbol = get_setting('site', 'global', 'currencysymbol')
    pricings = DirectoryPricing.objects.filter(status=1).order_by('duration')
    choices = []
    for pricing in pricings:
        if pricing.duration == 0:
            if is_admin(user):
                choice = (pricing.pk, 'Unlimited')
            else:
                continue
        else:
            if is_member(user):
                prices = "%s%s(R)/%s(P)" % (currency_symbol,pricing.regular_price_member, 
                                            pricing.premium_price_member)
            else:
                prices = "%s%s(R)/%s(P)" % (currency_symbol, pricing.regular_price, 
                                    pricing.premium_price)
            choice = (pricing.pk, '%d days for %s' % (pricing.duration, prices))
        choices.append(choice)
        
    return choices

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
  
def directory_set_inv_payment(user, directory, pricing): 
    if get_setting('module', 'directories', 'directoriesrequirespayment'):
        if not directory.invoice:
            inv = Invoice()
            inv.object_type = ContentType.objects.get(app_label=directory._meta.app_label, 
                                              model=directory._meta.module_name)
            inv.object_id = directory.id
            profile = user.get_profile()
            inv.title = "Directory Add Invoice"
            inv.bill_to = '%s %s' % (user.first_name, user.last_name)
            inv.bill_to_first_name = user.first_name
            inv.bill_to_last_name = user.last_name
            inv.bill_to_company = profile.company
            inv.bill_to_address = profile.address
            inv.bill_to_city = profile.city
            inv.bill_to_state = profile.state
            inv.bill_to_zip_code = profile.zipcode
            inv.bill_to_country = profile.country
            inv.bill_to_phone = profile.phone
            inv.bill_to_fax = profile.fax
            inv.bill_to_email = profile.email
            inv.ship_to = inv.bill_to
            inv.ship_to_first_name = user.first_name
            inv.ship_to_last_name = user.last_name
            inv.ship_to_company = profile.company
            inv.ship_to_address = profile.address
            inv.ship_to_city = profile.city
            inv.ship_to_state = profile.state
            inv.ship_to_zip_code = profile.zipcode
            inv.ship_to_country = profile.country
            inv.ship_to_phone = profile.phone
            inv.ship_to_fax = profile.fax
            inv.ship_to_email = profile.email
            inv.terms = "Due on Receipt"
            inv.due_date = datetime.now()
            inv.ship_date = datetime.now()
            inv.message = 'Thank You.'
            inv.status = True
            
            inv.total = get_directory_price(user, directory, pricing)
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
                    
            
def get_directory_price(user, directory, pricing):
    directory_price = 0
    if is_member(user):
        if directory.list_type == 'regular':
            return  pricing.regular_price_member
        else:
            return pricing.premium_price_member
    else:
        if directory.list_type == 'regular':
            return  pricing.regular_price
        else:
            return pricing.premium_price
                
