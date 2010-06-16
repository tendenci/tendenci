import time
import hmac
from django.conf import settings
from forms import SIMPaymentForm

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
    x_fp_hash = get_fingerprint(payment.id, x_fp_timestamp, x_amount)
    
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
              'x_address':payment.x_address,
              'x_city':payment.x_city,
              'x_state':payment.x_state,
              'x_zip':payment.x_zip,
              'x_country':payment.x_country,
              'x_ship_to_first_name':payment.x_ship_to_first_name,
              'x_ship_to_last_name':payment.x_ship_to_last_name,
              'x_ship_to_company':payment.x_ship_to_company,
              'x_ship_to_address':payment.x_ship_to_address,
              'x_ship_to_city':payment.x_ship_to_city,
              'x_ship_to_state':payment.x_ship_to_state,
              'x_ship_to_zip':payment.x_ship_to_zip,
              'x_ship_to_country':payment.x_ship_to_country,
              'x_fax':payment.x_fax,
              'x_phone':payment.x_phone,
              'x_show_form':'payment_form',
              #'x_logo_URL':getSetting("global", "MerchantLogo"),
        }
    form = SIMPaymentForm(initial=params)
    
    return form
