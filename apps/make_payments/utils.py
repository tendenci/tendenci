from invoices.models import Invoice

def make_payment_inv_add(user, make_payment, **kwargs):
    inv = Invoice()
    inv.assign_make_payment_info(user, make_payment)
    inv.estimate = True
    inv.status_detail = 'estimate'
    if kwargs.has_key('object_type'):
        inv.invoice_object_type = kwargs['object_type']
    else:
        inv.invoice_object_type = 'make_payment'
    inv.invoice_object_type_id = make_payment.id
    inv.subtotal = make_payment.payment_amount
    inv.total = make_payment.payment_amount
    inv.balance = make_payment.payment_amount
    
    inv.save(user)
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
    
    
    

    