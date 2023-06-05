import time
import hmac
import requests
import hashlib
import re
from django.conf import settings
from django.http import Http404
from django.db import transaction
from django.urls import reverse

from .forms import SIMPaymentForm
from tendenci.apps.payments.models import Payment
from tendenci.apps.payments.utils import payment_processing_object_updates
from tendenci.apps.payments.utils import log_payment, send_payment_notice
from tendenci.apps.site_settings.utils import get_setting


class AuthNetAPI:
    def __init__(self):
        self.headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        self.api_endpoint = settings.AUTHNET_API_ENDPOINT
        self.merchant_authentication = {"name": settings.MERCHANT_LOGIN,
                                        "transactionKey": settings.MERCHANT_TXN_KEY}

    def post_requests(self, request_dict):
        return requests.post(self.api_endpoint, headers=self.headers, json=request_dict)

    def process_response(self, res):
        """
        Process response.
        Returns (Success, code, text, res_dict)
        """
        if res.ok:
            res_dict = res.json()
            result_code = res_dict['messages']['resultCode']
            code = res_dict['messages']['message'][0]['code']
            text = res_dict['messages']['message'][0]['text']
            if result_code == 'Ok':
                return True, code, text, res_dict
            return False, code, text, res_dict
        return False, '', str(res.status_code), {}

    def get_public_client_key(self):
        """
        Get the public client key
        """
        request_dict = {
            "getMerchantDetailsRequest": {
                "merchantAuthentication": self.merchant_authentication
            }  
        }
        res = self.post_requests(request_dict)
        success, code, text, res_dict = self.process_response(res)
        if success:
            return res_dict['publicClientKey']
        return ''

    def create_customer_profile_from_trans(self, trans_id):
        """
        Create customer profile from a transaction (for membership auto renewal)
        
        return (customer_profile_id, customer_payment_profile_id_list)
        """
        request_dict = {
            "createCustomerProfileFromTransactionRequest": {
                "merchantAuthentication": self.merchant_authentication,
                "transId": trans_id
            }
        }
        res = self.post_requests(request_dict)
        success, code, text, res_dict = self.process_response(res)
        if success:
            return res_dict['customerProfileId'], res_dict['customerPaymentProfileIdList']

    def charge_customer_profile(self, payment, customer_profile_id, payment_profile_id):
        """
        Authorize and capture a payment using a stored customer payment profile.
        return (success, code, text, res_dict)
    
        https://developer.authorize.net/api/reference/index.html#payment-transactions-charge-a-customer-profile
        """
        request_dict = {
            "createTransactionRequest": {
                "merchantAuthentication": self.merchant_authentication,
                "refId": str(payment.id),
                "transactionRequest": {
                    "transactionType": "authCaptureTransaction",
                    "amount": str(payment.invoice.balance),
                    "currencyCode": get_setting('site', 'global', 'currency'),
                      "profile": {
                          "customerProfileId": customer_profile_id,
                          "paymentProfile": { "paymentProfileId": payment_profile_id }
                      },
                    "order": {
                        "invoiceNumber": str(payment.invoice.id),
                        "description": payment.description
                    }
                }
            }    
        }
        res = self.post_requests(request_dict)
        return self.process_response(res)

    def get_customer_payment_profiles(self, customer_profile_id):
        request_dict = {
            "getCustomerProfileRequest": {
                "merchantAuthentication": self.merchant_authentication,
                "customerProfileId": customer_profile_id,
                "includeIssuerInfo": "false"
            }
        }
        res = self.post_requests(request_dict)
        success, code, text, res_dict = self.process_response(res)
        if success:
            if 'paymentProfiles' in res_dict['profile']:
                payment_profiles = res_dict['profile']['paymentProfiles']
                return payment_profiles
        return []

    def validate_customer_payment_profile(self, customer_profile_id,
                                           customer_payment_profile_id):
        if hasattr(settings, 'AUTHNET_CIM_TEST_MODE') and settings.AUTHNET_CIM_TEST_MODE:
            validate_mode = 'testMode'
        else:
            validate_mode = 'liveMode'
        request_dict = {
            "validateCustomerPaymentProfileRequest": {
                "merchantAuthentication": self.merchant_authentication,
                "customerProfileId": customer_profile_id,
                 "customerPaymentProfileId": customer_payment_profile_id,
                 "validationMode": validate_mode
            }
        }
        res = self.post_requests(request_dict)
        success, code, text, res_dict = self.process_response(res)
        if success:
            direct_response = res_dict['directResponse'].split(',')
            # response_code == response_reason_code == 1 
            if direct_response[0] == direct_response[1] == '1':
                # approved == valid
                return True

        return False
   

    def get_token(self, customer_profile_id):
        """
        Get token using getHostedProfilePageRequest method
        Return a tuple: (token, error message or '')
        
        https://developer.authorize.net/api/reference/index.html#customer-profiles-get-accept-customer-profile-page
        """
        iframe_communicator_url = get_setting('site', 'global', 'siteurl') + \
                                 reverse('recurring_payment.authnet.iframe_communicator')
        request_dict = {
            "getHostedProfilePageRequest": {
                "merchantAuthentication": self.merchant_authentication,
                "customerProfileId": customer_profile_id,
                "hostedProfileSettings": {
                    "setting": [
                        {
                            "settingName": "hostedProfileIFrameCommunicatorUrl",
                            "settingValue": iframe_communicator_url
                        },
                        {
                            "settingName": "hostedProfilePageBorderVisible",
                            "settingValue": "true"
                        }
                    ]
                }
            }
        }
        res = self.post_requests(request_dict)
        success, code, text, res_dict = self.process_response(res)

        if success:
            return res_dict.get('token'), ''

        if code:
            return '', f'{code}:{text}'
    
        return '', str(res.status_code)  

    def delete_customer_profile(self, customer_profile_id):
        request_dict = {
            "deleteCustomerProfileRequest": {
                "merchantAuthentication": self.merchant_authentication,
                "customerProfileId": customer_profile_id
            }
        }
        res = self.post_requests(request_dict)
        return self.process_response(res)

    def create_customer_profile(self, **opt_d):
        """
        Take a dict which includes 'user_id', 'email' and 'description',
        return a tuple (success, customer_profile_id, message list)
        """
        res = self.create_customer_profile_request(**opt_d)
        success, code, text, res_dict = self.process_response(res)
        if success:
            return self.create_customer_profile_response(res_dict)
        return False, None, None

    def create_customer_profile_request(self, **opt_d):
        user_id = opt_d.get('user_id')
        email = opt_d.get('email')
        description = opt_d.get('description', '')
        request_dict = {
            "createCustomerProfileRequest": {
                "merchantAuthentication": self.merchant_authentication,
                "profile": {
                    "merchantCustomerId": user_id,
                    "description": description,
                    "email": email,
                }
            }
        }
        return self.post_requests(request_dict)

    def create_customer_profile_response(self, res_dict):
        """
        Parse the result from createCustomerProfileRequest,
        and return customerProfileId
        """
        if res_dict['messages']['resultCode'] == 'Ok':
            return True, res_dict['customerProfileId'], res_dict['messages']['message']
        
        # check if a customer profile already exist
        if res_dict['messages']['message'][0]['code'] == 'E00039':
            text = res_dict['messages']['message'][0]['text']
            p = re.compile(r'A duplicate record with ID (\d+) already exists.', re.I)
            match = p.search(text)
            if match:
                return True, match.group(1), res_dict['messages']['message'] 
        return False, None, res_dict['messages']['message']

    def create_txn_request(self, payment, opaque_value, opaque_descriptor):
        request_dict = {
            "createTransactionRequest": {
                "merchantAuthentication": self.merchant_authentication,
                "refId": str(payment.id),
                "transactionRequest": {
                    "transactionType": "authCaptureTransaction",
                    "amount": payment.amount,
                    "payment": {
                        "opaqueData": {
                            "dataDescriptor": opaque_descriptor,
                            "dataValue": opaque_value
                        }
                    },
                   "order": {
                    "invoiceNumber": payment.invoice.id,
                    "description": payment.description
                    },
                    "shipTo": {
                        "firstName": payment.ship_to_first_name,
                        "lastName": payment.ship_to_last_name,
                        "company": payment.ship_to_company,
                        "address": payment.ship_to_address,
                        "city": payment.ship_to_city,
                        "state": payment.ship_to_state,
                        "zip": payment.ship_to_zip,
                        "country": payment.ship_to_country
                    }
                }
            }
        }
        return self.post_requests(request_dict)
    
    def process_txn_response(self, user, res_dict, payment):
        """
        1. Update payment (equivalent to the old payment_update_authorizenet)
        2. Update object - call payment_processing_object_updates(request, payment)
        """
        ref_id = res_dict.get('refId', '')
        if str(payment.id) == ref_id:
            if res_dict['messages']['resultCode'] == 'Ok':
                tran_response = res_dict['transactionResponse']
                payment.response_code = tran_response['responseCode']
                if payment.response_code == '1':
                    if 'messages' in tran_response:
                        payment.response_reason_code = tran_response['messages'][0]['code']
                        payment.response_reason_text = tran_response['messages'][0]['description']
                else:
                    if 'errors' in tran_response:
                        payment.response_reason_code = tran_response['errors'][0]['errorCode']
                        payment.response_reason_text = tran_response['errors'][0]['errorText']
                payment.trans_id = tran_response['transId']
                payment.card_type = tran_response['accountType']
                payment.account_number = ''
                payment.auth_code = tran_response['authCode']
                payment.avs_code = tran_response['authCode']
                
                if payment.response_code == '1': # Approved
                    payment.mark_as_paid()
                    payment.save()
                    payment.invoice.make_payment(user, payment.amount)
                elif payment.response_code == '2': # Declined:
                    payment.status_detail = 'declined'
                    payment.save()
                elif payment.response_code == '3': # Error:
                    payment.status_detail = 'error'
                    payment.save()
                elif payment.response_code == '4': # Held for Review:
                    payment.status_detail = 'held_for_review'
                    payment.save()
            else:
                # Error
                if payment.status_detail == '':
                    payment.status_detail = 'not approved'
                payment.save()


def get_fingerprint(x_fp_sequence, x_fp_timestamp, x_amount):
    msg = '^'.join([settings.MERCHANT_LOGIN,
           x_fp_sequence,
           x_fp_timestamp,
           x_amount
           ])+'^'

    return hmac.new(settings.MERCHANT_TXN_KEY.encode(), msg.encode(), digestmod=hashlib.md5).hexdigest()


def get_form_token(request, payment):
    request_dict = {
          "getHostedPaymentPageRequest": {
            "merchantAuthentication": {
              "name": settings.MERCHANT_LOGIN,
              "transactionKey": settings.MERCHANT_TXN_KEY
            },
            "transactionRequest": {
              "transactionType": "authCaptureTransaction",
              "amount": "%.2f" % payment.amount,
              "customer": {
                "email": payment.email
              },
              "billTo": {
                "firstName": payment.first_name,
                "lastName": payment.last_name,
                "company": payment.company,
                "address": payment.address,
                "city": payment.city,
                "state": payment.state,
                "zip": payment.zip,
                "country": payment.country
              }
            },
            "hostedPaymentSettings": {
              "setting": [{
                "settingName": "hostedPaymentReturnOptions",
                "settingValue": "{\"showReceipt\": false}"
              }, {
                "settingName": "hostedPaymentButtonOptions",
                "settingValue": "{\"text\": \"Pay\"}"
              }, {
                "settingName": "hostedPaymentStyleOptions",
                "settingValue": "{\"bgColor\": \"blue\"}"
              }, {
                "settingName": "hostedPaymentPaymentOptions",
                "settingValue": "{\"cardCodeRequired\": true, \"showCreditCard\": true, \"showBankAccount\": false}"
              }, {
                "settingName": "hostedPaymentSecurityOptions",
                "settingValue": "{\"captcha\": false}"
              }, {
                "settingName": "hostedPaymentShippingAddressOptions",
                "settingValue": "{\"show\": false, \"required\": false}"
              }, {
                "settingName": "hostedPaymentBillingAddressOptions",
                "settingValue": "{\"show\": true, \"required\": false}"
              }, {
                "settingName": "hostedPaymentCustomerOptions",
                "settingValue": "{\"showEmail\": false, \"requiredEmail\": false, \"addPaymentProfile\": false}"
              }, {
                "settingName": "hostedPaymentOrderOptions",
                "settingValue": "{\"show\": true, \"merchantName\": \"" + get_setting('site', 'global', 'sitedisplayname') + "\"}"
              }, {
                "settingName": "hostedPaymentIFrameCommunicatorUrl",
                "settingValue": "{\"url\": \"" + get_setting('site', 'global', 'siteurl') + reverse('authorizenet.iframe_communicator') + "\"}"
              }]
            }
          }
        }
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    api_endpoint = settings.AUTHNET_API_ENDPOINT
    r = requests.post(api_endpoint, headers=headers, json=request_dict)
    #return r
    if r.ok:
        res_dict = r.json()
        if res_dict['messages']['resultCode'] == 'Ok':
            return res_dict['token']
    return None


# delete later
def prepare_authorizenet_sim_form(request, payment):
    x_fp_timestamp = str(int(time.time()))
    x_amount = "%.2f" % payment.amount
    x_fp_hash = get_fingerprint(str(payment.id), x_fp_timestamp, x_amount)
    x_logo_URL = get_setting('site', 'global', 'merchantlogo')

    params = {
              'x_fp_sequence':payment.id,
              'x_fp_timestamp':x_fp_timestamp,
              'x_fp_hash':x_fp_hash,
              'x_amount':x_amount,
              'x_version':'3.1',
              'x_login':settings.MERCHANT_LOGIN,
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


# delete later
def verify_hash(signature_key, response_d):
    if not signature_key:
        return False
    
    sha2_hash = response_d.get('x_SHA2_Hash', '')

    text_to_hash = ''
    # https://www.authorize.net/content/dam/authorize/documents/SIM_guide.pdf
    fields = ['x_trans_id', 'x_test_request', 'x_response_code', 'x_auth_code', 'x_cvv2_resp_code',
              'x_cavv_response', 'x_avs_code', 'x_method', 'x_account_number', 'x_amount',
              'x_company', 'x_first_name', 'x_last_name', 'x_address', 'x_city',
              'x_state', 'x_zip', 'x_country', 'x_phone', 'x_fax',
              'x_email', 'x_ship_to_company', 'x_ship_to_first_name', 'x_ship_to_last_name', 'x_ship_to_address',
              'x_ship_to_city', 'x_ship_to_state', 'x_ship_to_zip', 'x_ship_to_country', 'x_invoice_num',]
    for field in fields:
        text_to_hash += '^' + response_d.get(field, '')
    text_to_hash += '^'

    computed_hash = hmac.new(bytes.fromhex(signature_key),
                    text_to_hash.encode('utf-8'), hashlib.sha512).hexdigest().upper()
    return sha2_hash == computed_hash

    
# delete later
def authorizenet_thankyou_processing(request, response_d, **kwargs):
    from django.shortcuts import get_object_or_404

    x_invoice_num = response_d.get('x_invoice_num', 0)
    try:
        x_invoice_num = int(x_invoice_num)
    except:
        x_invoice_num = 0

    with transaction.atomic():
        payment = get_object_or_404(Payment.objects.select_for_update(), pk=x_invoice_num)

        # Verify hash to ensure the response is securely received from authorize.net.
        # Client needs to get the Signature Key in their Authorize.Net account
        # and assign the key to the settings.py AUTHNET_SIGNATURE_KEY
        signature_key = settings.AUTHNET_SIGNATURE_KEY
        if signature_key:
            is_valid_hash = verify_hash(signature_key, response_d)
            if not is_valid_hash:
                raise Http404

        if not payment.is_approved:  # if not already processed
            payment_update_authorizenet(request, response_d, payment)
            payment_processing_object_updates(request, payment)

            # log an event
            log_payment(request, payment)

            # send payment recipients notification
            send_payment_notice(request, payment)

        return payment

# delete later
def payment_update_authorizenet(request, response_d, payment, **kwargs):
    from decimal import Decimal
    payment.response_code = response_d.get('x_response_code', '')
    payment.response_subcode = response_d.get('x_response_subcode', '')
    payment.response_reason_code = response_d.get('x_response_reason_code', '')
    payment.response_reason_text = response_d.get('x_response_reason_text', '')
    payment.trans_id = response_d.get('x_trans_id', '')
    payment.card_type = response_d.get('x_card_type', '')
    # last 4 digits only
    payment.account_number = response_d.get('x_account_number', '')[-4:]
    payment.auth_code = response_d.get('x_auth_code', '')
    payment.avs_code = response_d.get('x_avs_code', '')
    # replace the data captured from authnet in case they changed from there.
    payment.amount = Decimal(response_d.get('x_amount', 0))
    payment.md5_hash = response_d.get('x_MD5_Hash', '')
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
