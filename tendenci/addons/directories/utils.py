# settings - directoriespaymenttypes, directoriesrequirespayment
from datetime import datetime
from cStringIO import StringIO
from PIL import Image
from django.contrib.contenttypes.models import ContentType
from tendenci.addons.directories.models import DirectoryPricing
from tendenci.apps.invoices.models import Invoice
from tendenci.core.payments.models import Payment
from tendenci.core.site_settings.utils import get_setting
from tendenci.libs.storage import get_default_storage


def resize_s3_image(image_path, width=200, height=200):
    """
    Resize an image on s3. 
    The image_path is the relative path to the media storage.
    """
    storage = get_default_storage()
    f = storage.open(image_path)
    content = f.read()
    f.close()
    img = Image.open(StringIO(content))
    img.thumbnail((width,height),Image.ANTIALIAS)
    f = storage.open(image_path, 'w')
    img.save(f)
    f.close()

def get_duration_choices(user):
    currency_symbol = get_setting('site', 'global', 'currencysymbol')
    pricings = DirectoryPricing.objects.filter(status=True).order_by('duration')
    choices = []
    for pricing in pricings:
        if pricing.duration == 0:
            if user.profile.is_superuser:
                choice = (pricing.pk, 'Unlimited')
            else:
                continue
        else:
            if pricing.show_member_pricing and user.profile.is_member:
                prices = "%s%s(R)/%s(P)" % (currency_symbol,pricing.regular_price_member, 
                                            pricing.premium_price_member)
            else:
                prices = "%s%s(R)/%s(P)" % (currency_symbol, pricing.regular_price, 
                                    pricing.premium_price)
            choice = (pricing.pk, '%d days for %s' % (pricing.duration, prices))
        choices.append(choice)
        
    return choices

def get_payment_method_choices(user):
    if user.profile.is_superuser:
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
            inv.bill_to_email = user.email
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
            inv.ship_to_email = user.email
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
            
            # tender the invoice
            inv.tender(user)
            
            # update job
            directory.invoice = inv
            directory.save()
            
            if user.profile.is_superuser:
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
    return pricing.get_price_for_user(
                      user=user,
                      list_type=directory.list_type)


def is_free_listing(user, pricing_id, list_type):
    """
    Check if a directory listing with the specified pricing and list type is free.
    """
    try:
        pricing_id = int(pricing_id)
    except:
        pricing_id = 0
    [pricing] = pricing_id and DirectoryPricing.objects.filter(pk=pricing_id)[:1] or [None]

    if pricing:
        return pricing.get_price_for_user(user, list_type=list_type) <= 0
    return False
