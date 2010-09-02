import time
import hmac
from django.conf import settings
from forms import SIMPaymentForm
from payments.models import Payment
from payments.utils import payment_processing_object_updates
from site_settings.utils import get_setting

def get_fingerprint(x_fp_sequence, x_fp_timestamp, x_amount):
    msg = '^'.join([settings.AUTHNET_LOGIN,
           x_fp_sequence,
           x_fp_timestamp,
           x_amount
           ])+'^'

    return hmac.new(settings.AUTHNET_KEY, msg).hexdigest()


def prepare_authorizenet_sim_form(request, payment):
    x_fp_timestamp = str(int(time.time()))
    x_amount = "%.2f" % payment.amount
    x_fp_hash = get_fingerprint(str(payment.id), x_fp_timestamp, x_amount)
    x_logo_URL = get_setting("site", "global", "MerchantLogo")
    
    params = {
              'x_fp_sequence':payment.id,
              'x_fp_timestamp':x_fp_timestamp,
              'x_fp_hash':x_fp_hash,
              'x_amount':x_amount,
              'x_version':'3.1',
              'x_login':settings.AUTHNET_LOGIN,
              'x_relay_response':'TRUE',
              'x_relay_url':payment.response_page,
              'x_invoice_num':payment.invoice_num,
              'x_description':payment.description,
              'x_email_customer':"True",
              'x_email':payment.email,
              'x_cust_id':payment.cust_id,
              'x_first_name':payment.first_name,
              'x_last_name':payment.last_name,
              'x_company':payment.company,
              'x_address':payment.address,
              'x_city':payment.city,
              'x_state':payment.state,
              'x_zip':payment.zip,
              'x_country':payment.country,
              'x_ship_to_first_name':payment.ship_to_first_name,
              'x_ship_to_last_name':payment.ship_to_last_name,
              'x_ship_to_company':payment.ship_to_company,
              'x_ship_to_address':payment.ship_to_address,
              'x_ship_to_city':payment.ship_to_city,
              'x_ship_to_state':payment.ship_to_state,
              'x_ship_to_zip':payment.ship_to_zip,
              'x_ship_to_country':payment.ship_to_country,
              'x_fax':payment.fax,
              'x_phone':payment.phone,
              'x_show_form':'payment_form',
              'x_logo_URL':x_logo_URL,
        }
    form = SIMPaymentForm(initial=params)
    
    return form

def authorizenet_thankyou_processing(request, response_d, **kwargs):
    from django.shortcuts import get_object_or_404

    x_invoice_num = response_d.get('x_invoice_num', 0)
    try:
        x_invoice_num = int(x_invoice_num)
    except:
        x_invoice_num = 0
    payment = get_object_or_404(Payment, pk=x_invoice_num)
    
    if payment.invoice.balance > 0:     # if balance=0, it means already processed
        payment_update_authorizenet(request, response_d, payment)
        payment_processing_object_updates(request, payment)
    return payment
        
def payment_update_authorizenet(request, response_d, payment, **kwargs):
    from decimal import Decimal
    payment.response_code = response_d.get('x_response_code', '')
    payment.response_subcode = response_d.get('x_response_subcode', '')
    payment.response_reason_code = response_d.get('x_response_reason_code', '')
    payment.response_reason_text = response_d.get('x_response_reason_text', '')
    payment.trans_id = response_d.get('x_trans_id', '')
    payment.auth_code = response_d.get('x_auth_code', '')
    payment.avs_code = response_d.get('x_avs_code', '')
    # replace the data captured from authnet in case they changed from there.
    payment.amount = Decimal(response_d.get('x_amount', 0))
    payment.first_name = response_d.get('x_first_name', '')
    payment.last_name = response_d.get('x_last_name', '')
    payment.company = response_d.get('x_company', '')
    payment.address = response_d.get('x_address', '')
    payment.city = response_d.get('x_city', '')
    payment.state = response_d.get('x_state', '')
    payment.country = response_d.get('x_country', '')
    payment.phone = response_d.get('x_phone', '')
    payment.fax = response_d.get('x_fax', '')
    payment.email = response_d.get('x_email', '')
    payment.ship_to_first_name = response_d.get('x_ship_to_first_name', '')
    payment.ship_to_last_name = response_d.get('x_ship_to_last_name', '')
    payment.ship_to_company = response_d.get('x_ship_to_company', '')
    payment.ship_to_address = response_d.get('x_ship_to_address', '')
    payment.ship_to_city = response_d.get('x_ship_to_city', '')
    payment.ship_to_state = response_d.get('x_ship_to_state', '')
    payment.ship_to_zip = response_d.get('x_ship_to_zip', '')
    payment.ship_to_country = response_d.get('x_ship_to_country', '')
    
    
    if payment.is_approved:
        payment.mark_as_paid()
        payment.save()
        payment.invoice.make_payment(request.user, payment.amount)
    else:
        if payment.status_detail == '':
            payment.status_detail = 'not approved'
            payment.save()
            
    
    
    
