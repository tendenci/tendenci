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
    

    