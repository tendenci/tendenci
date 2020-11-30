import re
from django.conf import settings
from django.urls import reverse
from tendenci.apps.site_settings.utils import get_setting

direct_response_fields = (
                        'response_code',
                        'response_subcode',
                        'response_reason_code',
                        'response_reason_text',
                        'auth_code',
                        'avs_code',
                        'trans_id',
                        'invoice_num',
                        'description',
                        'amount',
                        'method',
                        'trans_type',
                        'customer_id',
                        'first_name',
                        'last_name',
                        'company',
                        'address',
                        'city',
                        'state',
                        'zip',
                        'country',
                        'phone',
                        'fax',
                        'email',
                        'ship_to_first_name',
                        'ship_to_last_name',
                        'ship_to_company',
                        'ship_to_address',
                        'ship_to_city',
                        'ship_to_state',
                        'ship_to_zip',
                        'ship_to_country',
                        'tax',
                        'duty',
                        'freight',
                        'tax_exempt',
                        'purchase_order_number',
                        'md5_hash',
                        'card_code_response',
                        'cardholder_auth_verification',
                        'response',
                        'account_number',
                        'card_type',
                        'split_tender_id',
                        'requested_amount',
                        'balance_on_card',
                          )


def direct_response_dict(direct_response_str):
    """
    Return a dictionary from a direct response string.
    """
#    direct_response_str = "1,1,1,This transaction has been" + \
#        "approved.,000000,Y,2000000001,INV000001,description of" + \
#        "transaction,10.95,CC,auth_capture,custId123,John,Doe,,123 Main" + \
#        "St.,Bellevue,WA,98004,USA,000-000-" + \
#        "0000,,mark@example.com,John,Doe,,123 Main St.,Bellevue,WA,98004,USA,1.00,0.00,2.00,FALSE,PONUM000001," + \
#        "D18EB6B211FE0BBF556B271FDA6F92EE,M,2,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
    response_dict = {}
    max_length = len(direct_response_fields)
    # the x_delim_char we specified is || (in cim.py)
    # the delimiter in the response_code WAS comma, but now it's ||
    direct_response_list = direct_response_str.split('||')
    for i, value in enumerate(direct_response_list):
        if i < max_length:
            response_dict[direct_response_fields[i]] = value

    return response_dict

def payment_update_from_response(payment, direct_response_str):
    """
    Update the payment entry with the direct response from payment gateway.
    """
    response_dict = direct_response_dict(direct_response_str)
    for key in response_dict:
        if hasattr(payment, key):
            setattr(payment, key, response_dict[key])

    return payment


def to_camel_case(d):
    """
    Convert all keys in d dictionary from underscore_format to
    camelCaseFormat and return the new dict
    """
    if type(d) is dict:

        def to_upper(match):
            return match.group(1).upper()

        def to_camel(x):
            return re.sub(r'_([a-z])', to_upper, x)

        return dict([(to_camel(x[0]), x[1]) for x in d.items()])
    return d


def get_test_mode():
    """Return test_mode (false/true) - to be used in js
    """
    test_mode = 'false'
    if hasattr(settings, 'AUTHNET_CIM_TEST_MODE') and  settings.AUTHNET_CIM_TEST_MODE:
        test_mode = 'true'

    return test_mode

def get_token(rp, CIMCustomerProfile, CIMHostedProfilePage, iframe_communicator_url='', is_secure=False):
    """Get the token from payment gateway for this customer (ex: customer_profile_id=4356210).
       Return token and gateway_error
    """
    gateway_error = False

    site_url = get_setting('site', 'global', 'siteurl')
    if is_secure:
        site_url = site_url.replace('http://', 'https://')
    if not iframe_communicator_url:
        iframe_communicator_url = '%s%s' % (
                                site_url,
                                reverse('recurring_payment.authnet.iframe_communicator'))

    token = ""
    if not rp.customer_profile_id:
        # customer_profile is not available yet for this customer, create one now
        cp = CIMCustomerProfile()
        d = {'email': rp.user.email,
             'description': rp.description,
             'customer_id': str(rp.id)}
        success, response_d = cp.create(**d)
        if success:
            rp.customer_profile_id = response_d['customer_profile_id']
            rp.save()
        else:
            gateway_error = True
            # return since we can't continue without a profile id
            return token, gateway_error

    hosted_profile_page = CIMHostedProfilePage(rp.customer_profile_id)
    hosted_profile_validation_mode = 'liveMode'

    d = {'hosted_profile_settings':
         {'hosted_profile_heading_bg_color': '#e0e0e0',     # the bg color of sections can be customized
          'hosted_profile_card_code_required': 'true',
          'hosted_profile_validation_mode': hosted_profile_validation_mode,
         'hosted_profile_iFrame_communicator_url': '%s' % iframe_communicator_url}}
    success, response_d = hosted_profile_page.get(**d)
    #print success, response_d

    if not success:
        gateway_error = True
    else:
        token = response_d['token']

    return token, gateway_error
