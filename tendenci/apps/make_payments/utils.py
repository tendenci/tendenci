from datetime import datetime
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from tendenci.apps.invoices.models import Invoice

def make_payment_inv_add(user, make_payment, **kwargs):
    inv = Invoice()
    # field to be populated to invoice
    inv.title = _("Make Payment Invoice")
    inv.bill_to =  make_payment.first_name + ' ' + make_payment.last_name
    inv.bill_to_first_name = make_payment.first_name
    inv.bill_to_last_name = make_payment.last_name
    inv.bill_to_company = make_payment.company
    inv.bill_to_address = '%s %s' % (make_payment.address,
                                     make_payment.address2)
    inv.bill_to_city = make_payment.city
    inv.bill_to_state =  make_payment.state
    inv.bill_to_zip_code = make_payment.zip_code
    inv.bill_to_country = make_payment.country
    inv.bill_to_phone = make_payment.phone
    inv.bill_to_email = make_payment.email
    inv.ship_to =  make_payment.first_name + ' ' + make_payment.last_name
    inv.ship_to_first_name = make_payment.first_name
    inv.ship_to_last_name = make_payment.last_name
    inv.ship_to_company = make_payment.company
    inv.ship_to_address = '%s %s' % (make_payment.address,
                                     make_payment.address2)
    inv.ship_to_city = make_payment.city
    inv.ship_to_state = make_payment.state
    inv.ship_to_zip_code =  make_payment.zip_code
    inv.ship_to_country = make_payment.country
    inv.ship_to_phone =  make_payment.phone
    inv.ship_to_email = make_payment.email
    inv.terms = "Due on Receipt"
    inv.due_date = datetime.now()
    inv.ship_date = datetime.now()
    inv.message = 'Thank You.'
    inv.status = True

    inv.estimate = True
    inv.status_detail = 'estimate'
    inv.object_type = ContentType.objects.get(app_label=make_payment._meta.app_label, model=make_payment._meta.model_name)
    inv.object_id = make_payment.id
    inv.subtotal = make_payment.payment_amount
    inv.total = make_payment.payment_amount
    inv.balance = make_payment.payment_amount

    if user and not user.is_anonymous():
        inv.set_creator(user)
        inv.set_owner(user)

    inv.save(user)
    # tender the invoice
    inv.tender(user)
    make_payment.invoice_id = inv.id

    return inv

def make_payment_email_user(request, make_payment, invoice, **kwargs):
    from django.core.mail.message import EmailMessage
    from django.template.loader import render_to_string
    from django.conf import settings
    from django.template import RequestContext

    subject = render_to_string('make_payments/email_user_subject.txt',
                               {'make_payment':make_payment},
                               context_instance=RequestContext(request))
    body = render_to_string('make_payments/email_user.txt', {'make_payment':make_payment,
                                                             'invoice':invoice},
                                                             context_instance=RequestContext(request))
    sender = settings.DEFAULT_FROM_EMAIL
    recipient = make_payment.email
    msg = EmailMessage(subject, body, sender, [recipient])
    msg.content_subtype = 'html'
    try:
        msg.send()
    except:
        pass
