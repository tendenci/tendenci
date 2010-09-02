# settings: label, donationspaymenttypes, donationsallocations, 
#           donationsrecipients, 
from invoices.models import Invoice
from perms.utils import is_admin
from site_settings.utils import get_setting

def donation_inv_add(user, donation, **kwargs):
    inv = Invoice()
    inv.assign_donation_info(user, donation)
    inv.estimate = True
    inv.status_detail = 'estimate'
    if kwargs.has_key('object_type'):
        inv.invoice_object_type = kwargs['object_type']
    else:
        inv.invoice_object_type = 'donation'
    inv.invoice_object_type_id = donation.id
    inv.subtotal = donation.donation_amount
    inv.total = donation.donation_amount
    inv.balance = donation.donation_amount
    
    inv.save(user)
    donation.invoice = inv

    return inv

def donation_email_user(request, donation, invoice, **kwargs):
    from django.core.mail.message import EmailMessage
    from django.template.loader import render_to_string
    from django.conf import settings
    from django.template import RequestContext
    
    subject = render_to_string('donations/email_user_subject.txt', 
                               {'donation':donation},
                               context_instance=RequestContext(request))
    body = render_to_string('donations/email_user.txt', {'donation':donation,
                                                        'invoice':invoice},
                                                        context_instance=RequestContext(request))
    sender = settings.DEFAULT_FROM_EMAIL
    recipient = donation.email
    msg = EmailMessage(subject, body, sender, [recipient])
    msg.content_subtype = 'html'
    try:
        msg.send()
    except:
        pass

def get_payment_method_choices(user):
    if is_admin(user):
        return (('paid - check', 'User paid by check'),
                ('paid - cc', 'User paid by credit card'),
                ('Credit Card', 'Make online payment NOW'),)
    else:
        donation_payment_types = get_setting('module', 'donations', 'donationspaymenttypes')
        if donation_payment_types:
            donation_payment_types_list = donation_payment_types.split(',')
            donation_payment_types_list = [item.strip() for item in donation_payment_types_list]
            
            return [(item, item) for item in donation_payment_types_list]
        else:
            return ()
        
def get_allocation_choices(user, allocation_str):
    #allocation_str = get_setting('module', 'donations', 'donationsallocations')
    if allocation_str:
        allocation_list = allocation_str.split(',')
        allocation_list = [item.strip() for item in allocation_list]
        
        return [(item, item) for item in allocation_list]
    else:
        return ()
        
        

    
    
    

    