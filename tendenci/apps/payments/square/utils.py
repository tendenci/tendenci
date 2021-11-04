from tendenci import __version__ as tendenci_version

def payment_update_square(request, charge_response, payment):
    if hasattr(charge_response,'status') and charge_response.status == "COMPLETED":
        payment.status_detail = 'approved'
        payment.response_code = '1'
        payment.response_subcode = '1'
        payment.response_reason_code = '1'
        payment.response_reason_text = 'This transaction has been approved. (Created# %s)' % charge_response.created_at
        payment.trans_id = charge_response.id
    else:
        payment.response_code = 0
        payment.response_reason_code = 0
        payment.response_reason_text = charge_response

    if payment.is_approved:
        payment.mark_as_paid()
        payment.save()
        payment.invoice.make_payment(request.user, payment.amount)
    else:
        if payment.status_detail == '':
            payment.status_detail = 'not approved'
        payment.save()
