#import time
from django.conf import settings
#from django.http import Http404
from forms import FirstDataPaymentForm
from payments.models import Payment
from payments.utils import payment_processing_object_updates
#from site_settings.utils import get_setting


def prepare_firstdata_form(request, payment):
    chargetotal = "%.2f" % payment.amount
    if request.user.is_authenticated():
        userid = request.user.id
    else:
        userid = 0
    
    params = {
              'storename':settings.MERCHANT_LOGIN,
              'mode':'payonly',
              'txntype':'sale',
              'oid':payment.id,
              'userid':userid,
              'bcountry':payment.country,
              'objectguid':payment.guid,
              'paymentid':payment.id,
              'invoiceid':payment.invoice.id,
              'chargetotal':chargetotal,
              'bname':'%s %s' % (payment.first_name, payment.last_name),
              'email':payment.email,
              'bcompany':payment.cust_id,
              'baddr1':payment.address,
              'baddr2':payment.address2,
              'bcity':payment.city,
              'bstate':payment.state,
              'fax':payment.fax,
              'phone':payment.phone,
              'shippingbypass':'true',
              'comments':payment.description,
        }
    form = FirstDataPaymentForm(initial=params)
    
    return form

def firstdata_thankyou_processing(request, response_d, **kwargs):
    from django.shortcuts import get_object_or_404

    paymentid = response_d.get('paymentid', 0)
    try:
        paymentid = int(paymentid)
    except:
        paymentid = 0
    payment = get_object_or_404(Payment, pk=paymentid)
    
    if payment.invoice.balance > 0:     # if balance==0, it means already processed
        payment_update_firstdata(request, response_d, payment)
        payment_processing_object_updates(request, payment)
    return payment
        
def payment_update_firstdata(request, response_d, payment, **kwargs):
    if payment.status_detail.lower() == 'approved':
        payment.response_code = 1
        payment.response_subcode = 1
        payment.response_reason_code = 1
        payment.response_reason_text = response_d.get('approval_code', '')
    else:
        payment.response_code = 0
        payment.response_reason_code = 0
        # need to verify the variable name "fail_reason" 
        #because in T4, it's "failReason", but in firstdata doc, it's "fail_reason"
        # http://www.firstdata.com/downloads/marketing-merchant/fd_globalgatewayinternetpaymentgatewayconnect_integrationguideemea.pdf
        payment.response_reason_text = response_d.get('fail_reason', '')
    
    
    if payment.is_approved:
        payment.mark_as_paid()
        payment.save()
        payment.invoice.make_payment(request.user, payment.amount)
    else:
        if payment.status_detail == '':
            payment.status_detail = 'not approved'
        payment.save()
            
    
    
    
