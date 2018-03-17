# settings: label, donationspaymenttypes, donationsallocations,
#           donationsrecipients,
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from tendenci.apps.invoices.models import Invoice
from tendenci.apps.site_settings.utils import get_setting

def donation_inv_add(user, donation, **kwargs):
    inv = Invoice()
    inv.title = "Donation Invoice"
    inv.bill_to = donation.first_name + ' ' + donation.last_name
    inv.bill_to_first_name = donation.first_name
    inv.bill_to_last_name = donation.last_name
    inv.bill_to_company = donation.company
    inv.bill_to_address = donation.address
    inv.bill_to_city = donation.city
    inv.bill_to_state = donation.state
    inv.bill_to_zip_code = donation.zip_code
    inv.bill_to_country = donation.country
    inv.bill_to_phone = donation.phone
    inv.bill_to_email = donation.email
    inv.ship_to = donation.first_name + ' ' + donation.last_name
    inv.ship_to_first_name = donation.first_name
    inv.ship_to_last_name = donation.last_name
    inv.ship_to_company = donation.company
    inv.ship_to_address = donation.address
    inv.ship_to_city = donation.city
    inv.ship_to_state = donation.state
    inv.ship_to_zip_code = donation.zip_code
    inv.ship_to_country = donation.country
    inv.ship_to_phone = donation.phone
    #self.ship_to_fax = make_payment.fax
    inv.ship_to_email =donation.email
    inv.terms = "Due on Receipt"
    inv.due_date = datetime.now()
    inv.ship_date = datetime.now()
    inv.message = 'Thank You.'
    inv.status = True

    inv.estimate = True
    inv.status_detail = 'tendered'
    inv.object_type = ContentType.objects.get(app_label=donation._meta.app_label,
                                              model=donation._meta.model_name)
    inv.object_id = donation.id
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

    subject = render_to_string(template_name='donations/email_user_subject.txt',
                               context={'donation':donation},
                               request=request)
    body = render_to_string(template_name='donations/email_user.txt', context={'donation':donation,
                                                        'invoice':invoice},
                                                        request=request)
    sender = settings.DEFAULT_FROM_EMAIL
    recipient = donation.email
    msg = EmailMessage(subject, body, sender, [recipient])
    msg.content_subtype = 'html'
    try:
        msg.send()
    except:
        pass

def get_payment_method_choices(user):
    if user.profile.is_superuser:
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

def get_preset_amount_choices(preset_amount_str):
    if preset_amount_str:
        preset_amount_list = preset_amount_str.split(',')
        preset_amount_list = [item.strip() for item in preset_amount_list]

        return [(item, item) for item in preset_amount_list]
    else:
        return ()
