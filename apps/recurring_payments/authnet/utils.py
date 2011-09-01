
import re

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
    direct_response_list = direct_response_str.split(',')
    for i, value in enumerate(direct_response_list):
        if i < max_length:
            response_dict[direct_response_fields[i]] = value
            
    return response_dict

def payment_update_from_response(payment, direct_response_str):
    """
    Update the payment entry with the direct response from payment gateway.
    """
    response_dict = direct_response_dict(direct_response_str)
    for key in response_dict.keys():
        if hasattr(payment, key):
            exec('payment.%s="%s"' % (key, response_dict[key]))
            
    return payment


def to_camel_case(d):
    """
	Convert all keys in d dictionary from underscore_format to
	camelCaseFormat and return the new dict
	"""
    if type(d) is dict:
        to_upper = lambda match: match.group(1).upper()
        to_camel = lambda x: re.sub("_([a-z])", to_upper, x)
        
        return dict(map(lambda x: (to_camel(x[0]), x[1]), d.items()))
    return d

