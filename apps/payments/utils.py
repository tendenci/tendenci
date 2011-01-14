
# update the object
def payment_processing_object_updates(request, payment, **kwargs):
    # they are paid, so update the object
    if str(payment.response_code) == '1' and str(payment.response_reason_code) == '1':
        obj = payment.invoice.get_object()
        if obj and hasattr(obj, 'auto_update_paid_object'):
            obj.auto_update_paid_object(request, payment)

            
