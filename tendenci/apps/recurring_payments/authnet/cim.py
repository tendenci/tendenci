import re
import urllib2
from xml.etree import ElementTree as ET

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from tendenci.addons.recurring_payments.authnet.utils import to_camel_case

BILL_TO_FIELDS = ('firstName', 'lastName', 'company', 'address', 'city', 'state', 'zip',
                  'country', 'phoneNumber', 'faxNumber')
CREDIT_CARD_FIELDS = ('cardNumber', 'expirationDate', 'cardCode')
TAX_FIELDS = ('amount', 'name', 'description')
SHIPPING_FIELDS = ('amount', 'name', 'description')
LINE_ITEMS_FIELDS = ('itemId', 'name', 'description', 'quantity', 'unitPrice', 'taxable')
ORDER_FIELDS = ('invoiceNumber', 'description', 'purchaseOrderNumber')
TRANSACTION_EXTRA_OPTIONS = {'x_delim_data': 'TRUE',
                            'x_delim_char': '||',
                            'x_encap_char': ''}


class CIMBase(object):
    """
    A base class to handle basic CIM request and response
    """
    def __init__(self):
        if hasattr(settings, 'AUTHNET_CIM_TEST_MODE') and  settings.AUTHNET_CIM_TEST_MODE:
            self.cim_url = settings.AUTHNET_CIM_API_TEST_URL
        else:
            self.cim_url = settings.AUTHNET_CIM_API_URL

    def create_base_xml(self, root_name,  **kwargs):
        """
        Create a basic xml file with the merchantAuthentication node.
        """
        root = ET.Element(root_name)
        root.set('xmlns', 'AnetApi/xml/v1/schema/AnetApiSchema.xsd')
        authentication = ET.SubElement(root, 'merchantAuthentication')
        name_e = ET.SubElement(authentication, 'name')
        name_e.text = settings.MERCHANT_LOGIN
        key_e = ET.SubElement(authentication, 'transactionKey')
        key_e.text = settings.MERCHANT_TXN_KEY

        return root

    def create_payment_profile_node(self, node_name, billing_info, credit_card_info,  **kwargs):
        # make payment_profiles node
        payment_profiles_node =  ET.Element(node_name)
        # bill_to
        billing_info = to_camel_case(billing_info)
        if billing_info and (type(billing_info) is dict):
            bill_to_node = ET.SubElement(payment_profiles_node, 'billTo')
            bill_to_node = self.build_node_from_dict(bill_to_node,
                                                     billing_info,
                                                     BILL_TO_FIELDS)

        # credit_card
        payment_node =  ET.SubElement(payment_profiles_node, 'payment')
        credit_card_info= to_camel_case(credit_card_info)
        if credit_card_info and (type(credit_card_info) is dict):
            credit_card_node = ET.SubElement(payment_node, 'creditCard')

            credit_card_node = self.build_node_from_dict(credit_card_node,
                                                         credit_card_info,
                                                         CREDIT_CARD_FIELDS)

        return payment_profiles_node

    def build_node_from_dict(self, parent_node, d, field_scope=None):
        for key in d.keys():
            if not field_scope or key in field_scope:
                value = d.get(key)
                node = ET.SubElement(parent_node, key)
                node.text = value
        return parent_node




    def process_request(self, xml_root):
        request_xml_str = '%s\n%s' % ('<?xml version="1.0" encoding="utf-8"?>', ET.tostring(xml_root))
        #print request_xml_str
        request = urllib2.Request(self.cim_url,
                                request_xml_str,
                                {'Content-Type': 'text/xml',
                                'encoding': 'utf-8'})
        response = urllib2.urlopen(request)
        data = response.read()

        return self.process_response(data)


    def process_response(self, raw_response_xml):
        """
        Extract the data from raw response xml to a dictionary.
        """
#        raw_response_xml = """<?xml version="1.0" encoding="utf-8"?>
#        <createCustomerProfileTransactionResponse
#        xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
#        <messages>
#        <resultCode>Ok</resultCode>
#        <message>
#        <code>I00001</code>
#        <text>Successful.</text>
#        </message>
#        </messages>
#        <directResponse>1,1,1,This transaction has been
#        approved.,000000,Y,2000000001,INV000001,description of
#        transaction,10.95,CC,auth_capture,custId123,John,Doe,,123 Main
#        St.,Bellevue,WA,98004,USA,000-000-
#        0000,,mark@example.com,John,Doe,,123 Main
#        St.,Bellevue,WA,98004,USA,1.00,0.00,2.00,FALSE,PONUM000001,
#        D18EB6B211FE0BBF556B271FDA6F92EE,M,2,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#        </directResponse>
#        </createCustomerProfileTransactionResponse>"""


        e = ET.XML(raw_response_xml)
        d = self._recurive_parse(e)
        success = (d['messages']['result_code'].lower() == 'ok')

        d['result_code'] = d['messages']['result_code']
        d['message_code'] = d['messages']['message']['code']
        d['message_text'] = d['messages']['message']['text']

        return success, d


    def _recurive_parse(self, element):
        """
        Recurively parse the xml tree until we reach to the end node.

        example output:

        {    'customerProfileId': '4356210',
            'customerPaymentProfileIdList':
                {'numericString': '3831946'},
            'messages':
                {'resultCode': 'Ok',
                 'message':
                     {'text': 'Successful.', 'code': 'I00001'}
                },
            'validationDirectResponseList': None,
            'customerShippingAddressIdList': None
        }
        """
        d = {}
        for sub_e in element:
            # remove the namespace in the tag
            # e.g.{AnetApi/xml/v1/schema/AnetApiSchema.xsd}resultCode
            name = re.sub(r'(\{.*?\})*(\w+)', r'\2', sub_e.tag)

            # convert camelCase to underscore
            name = re.sub('([A-Z])', lambda match: "_" + match.group(1).lower(), name)

            children = sub_e.getchildren()
            if not children:
                if d.has_key(name):
                    if not type(d[name]) is list:
                        d[name] = list([d[name]])
                    d[name].append(sub_e.text)
                else:
                    d[name] = sub_e.text
            else:
                d[name] = self._recurive_parse(sub_e)
        return d

class CIMCustomerProfile(CIMBase):
    def __init__(self, customer_profile_id=None):
        super(CIMCustomerProfile, self).__init__()

        self.customer_profile_id = customer_profile_id

    def create(self, **kwargs):
        """
        Create a customer profile on authorize.net
        Input fields:
            ref_id - optinal
            profile - required (either merchant_customer_id or email & description)
                merchant_customer_id
                description
                email
            payment_profiles - optinal
                customer_type - optinal
                bill_to
                    first_name, last_name, company, address, city, state, zip,
                    country, phone_number, fax_number,
                payment
                    credit_card, card_number, expiration_date, card_code, bank_account
            account_type - optinal
            rounting_number
            account_number
            name_on_account
            echeck_type
            bank_name
                ship_to_list
                    first_name, last_name, company, address, city, state, zip, country
            phone_number
            fax_number
            validation_mode

        Output fields:
            ref_id
            customer_profile_id
            customer_payment_profile_id_list
            customer_shippingaddress_id_list
            validation_direct_response_list

        Example call:

        >>> from recurring_payments.authnet.cim import CIMCustomerProfile
        >>> cp = CIMCustomerProfile()
        >>> d = {'email': 'jqian@schipul.com', 'description': 'self registration',
                    'credit_card_info': {'card_number': '4111111111111111',
                                        'expiration_date': '2015-12'}
                }
        >>> cp.create(**d)

        Sample request:

        <?xml version="1.0" encoding="utf-8"?>
        <createCustomerProfileRequest xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
            <merchantAuthentication>
                <name>2J5ke9T6</name>
                <transactionKey>2CrW543gWMAs32vM</transactionKey>
            </merchantAuthentication>
            <profile>
                <description>self registration</description><email>jqian@schipul.com</email>
                <paymentProfiles><payment><creditCard><cardNumber>4111111111111111</cardNumber>
                <expirationDate>2015-12</expirationDate></creditCard></payment></paymentProfiles>
                </profile>
        </createCustomerProfileRequest>

        Sample response:

        <?xml version="1.0" encoding="utf-8"?>
        <createCustomerProfileResponse xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="AnetApi/xml/v1/schema/AnetApiSchema.xsd">
            <messages>
                <resultCode>Ok</resultCode>
                <message>
                    <code>I00001</code>
                    <text>Successful.</text>
                </message>
            </messages>
            <customerProfileId>4356210</customerProfileId>
            <customerPaymentProfileIdList>
                <numericString>3831946</numericString>
            </customerPaymentProfileIdList>
            <customerShippingAddressIdList />
            <validationDirectResponseList />
        </createCustomerProfileResponse>


        """
        root_name = 'createCustomerProfileRequest'
        xml_root = self.create_base_xml(root_name)
        ref_id = kwargs.get('ref_id', '')
        if ref_id:
            ET.SubElement(xml_root, 'refId')

        profile_node = self.create_profile_node(**kwargs)
        xml_root.append(profile_node)

        return self.process_request(xml_root)


    def delete(self, **kwargs):
        """
        Delete an existing customer profile along with all
        associated customer payment profiles and customer
        shipping addresses.

        Input fields:
            refId - optional
            customer_profile_id
        """
        root_name = 'deleteCustomerProfileRequest'
        xml_root = self.create_base_xml(root_name)
        customer_profile_id_node = ET.SubElement(xml_root, 'customerProfileId')
        customer_profile_id_node.text = self.customer_profile_id

        return self.process_request(xml_root)



    def get(self, **kwargs):
        """
        Get a customer profile from authorize.net

        Input fields:
            customer_profile_id

        Output fields:


        """
        root_name = 'getCustomerProfileRequest'
        xml_root = self.create_base_xml(root_name)
        customer_profile_id_node = ET.SubElement(xml_root, 'customerProfileId')
        customer_profile_id_node.text = self.customer_profile_id

        return self.process_request(xml_root)

    def get_all(self, **kwargs):
        """
        Retrieve all existing customer profile Ids.

        Input fields:
            None
        Output fields:
            refId - optional
            ids

        """
        root_name = 'getCustomerProfileIdsRequest'
        xml_root = self.create_base_xml(root_name)
        return  self.process_request(xml_root)


    def update(self, **kwargs):
        """
        Update an existing customer profile on authorize.net.

        Input fields:
            refId - optional
            profile:
                merchant_customer_id - optional
                description - optional
                email - optional
                customer_profile_id

        Output fields:
            refId

        """
        kwargs['mode'] = 'update'
        root_name = 'updateCustomerProfileRequest'
        xml_root = self.create_base_xml(root_name)
        ref_id = kwargs.get('ref_id', '')
        if ref_id:
            ET.SubElement(xml_root, 'refId')

        profile_node = self.create_profile_node(**kwargs)
        xml_root.append(profile_node)

        return self.process_request(xml_root)


    def create_profile_node(self, **kwargs):
        customer_id = kwargs.get('customer_id', '')
        description = kwargs.get('description', '')
        email = kwargs.get('email', '')
        customer_profile_id = kwargs.get('customer_profile_id', '')
        mode = kwargs.get('mode', 'create')

        if mode == 'create':
            if not customer_id and not all([email, description]):
                raise AttributeError, _("Either custom_id or email and description are required fields.")
        else: # mode == 'update'
            if not customer_profile_id:
                raise AttributeError, _("The customer_profile_id is a required field.")

        profile_node = ET.Element("profile")
        if customer_id:
            customer_id_node = ET.SubElement(profile_node, 'merchantCustomerId')
            customer_id_node.text = customer_id
        if description:
            # profile description
            description_node = ET.SubElement(profile_node, 'description')
            description_node.text = description
        if email:
            email_node = ET.SubElement(profile_node, 'email')
            email_node.text = email
        if customer_profile_id:
            customer_profile_id_node = ET.SubElement(profile_node, 'customerProfileId')
            customer_profile_id_node.text = customer_profile_id

        if mode == 'create':
            # make payment_profiles node
            billing_info = kwargs.get('billing_info', '')
            credit_card_info= kwargs.get('credit_card_info', '')
            if billing_info or credit_card_info:
                payment_profiles_node = self.create_payment_profile_node('paymentProfiles',
                                                                         billing_info,
                                                                         credit_card_info)


                profile_node.append(payment_profiles_node)

        return profile_node


class CIMCustomerPaymentProfile(CIMBase):
    def __init__(self, customer_profile_id, customer_payment_profile_id=None):
        super(CIMCustomerPaymentProfile, self).__init__()

        self.customer_profile_id = customer_profile_id
        self.customer_payment_profile_id = customer_payment_profile_id


    def create(self, **kwargs):
        """
        Create a new customer payment profile for an existing customer profile.

        Input fields:
            ref_id - optional
            customer_profile_id
            payment_profile:
                customer_type - optional
                bill_to:
                    first_name, last_name, company, address, city , state, zip, country, phone_number, fax_number
                payment:
                    credit_card
                        card_number, expiration_date, card_code
            validation_mode: none, testMode, liveMode

        Output fields:
            ref_id
            customer_payment_profile_id
            validation_direct_response


        Example call:
        d = {'ref_id': 222,
             'billing_info':{'first_name': 'John',
                             'last_name': 'Doe',
                             'company': '',
                             'address': '123 Main St.',
                             'city': 'Bellevue',
                             'state': 'WA',
                             'zip': '98004',
                             'country': 'USA',
                             'phoneNumber': '000-111-0000'
                             'faxNumber':''
                             },
             'credit_card_info': {
                                'card_number': '4111111111111111',
                                'expiration_date': '2023-12',
                                '':
                                 }
        }

        cpp = CustomerPaymentProfile('4356210')
        cpp.create(**d)
        """

        if not self.customer_profile_id:
            raise AttributeError, "Missing customer_profile_id."

        root_name = 'createCustomerPaymentProfileRequest'
        xml_root = self.create_base_xml(root_name)
        ref_id = kwargs.get('ref_id', '')
        if ref_id:
            ET.SubElement(xml_root, 'refId')

        customer_profile_id_node = ET.SubElement(xml_root, 'customerProfileId')
        customer_profile_id_node.text = self.customer_profile_id

        billing_info = kwargs.get('billing_info', '')
        credit_card_info= kwargs.get('credit_card_info', '')
        if billing_info or credit_card_info:
            payment_profiles_node = self.create_payment_profile_node('paymentProfile',
                                                                     billing_info,
                                                                     credit_card_info)

            xml_root.append(payment_profiles_node)

        return  self.process_request(xml_root)


    def delete(self, **kwargs):
        """
        Delete a customer payment profile from an existing customer profile.

        Input fields:
            ref_id - optional
            customer_profile_id
            customer_payment_profile_id

       Output fields:
           ref_id - if included in the input

        """

        if not self.customer_profile_id or not self.customer_payment_profile_id:
            raise AttributeError, _("Missing customer_profile_id or customer_payment_profile_id.")

        root_name = 'deleteCustomerPaymentProfileRequest'
        xml_root = self.create_base_xml(root_name)
        customer_profile_id_node = ET.SubElement(xml_root, 'customerProfileId')
        customer_profile_id_node.text = self.customer_profile_id

        customer_payment_profile_id_node = ET.SubElement(xml_root, 'customerPaymentProfileId')
        customer_payment_profile_id_node.text = self.customer_payment_profile_id

        return self.process_request(xml_root)


    def get(self, **kwargs):
        """
        retrieve a customer payment profile for an existing customer profile.

        Input fields:
            customer_profile_id
            customer_payment_profile_id

        Output fields:
            customer_payment_profile_id
            payment_profile:
                customer_type
                bill_to:
                    first_name, last_name, company, address, city , state, zip, country, phone_number, fax_number
                payment:
                    credit_card
                        card_number, expiration_date, card_code

        """

        if not self.customer_profile_id or not self.customer_payment_profile_id:
            raise AttributeError, _("Missing customer_profile_id or customer_payment_profile_id in input.")

        root_name = 'getCustomerPaymentProfileRequest'
        xml_root = self.create_base_xml(root_name)
        customer_profile_id_node = ET.SubElement(xml_root, 'customerProfileId')
        customer_profile_id_node.text = self.customer_profile_id
        customer_payment_profile_id_node = ET.SubElement(xml_root, 'customerPaymentProfileId')
        customer_payment_profile_id_node.text = self.customer_payment_profile_id

        return self.process_request(xml_root)

    def update(self, **kwargs):
        """
        Update a customer payment profile for an existing customer profile.
        CAUTION - "If some elements in this request are not submitted or are submitted with a blank value, the
        values in the original profile are removed on authorize.net.
        "

        Input fields:
            ref_id - optional
            customer_profile_id
            payment_profile:
                customer_payment_profile_id
                customer_type - optional
                bill_to:
                    first_name, last_name, company, address, city , state, zip, country, phone_number, fax_number
                payment:
                    credit_card
                        card_number, expiration_date, card_code
            validation_mode: none, testMode, liveMode

        Output fields:
            ref_id if included
            validation_direct_response


        """
        if not self.customer_profile_id or not self.customer_payment_profile_id:
            raise AttributeError, _("Missing customer_profile_id or customer_payment_profile_id in input.")

        root_name = 'updateCustomerPaymentProfileRequest'
        xml_root = self.create_base_xml(root_name)
        customer_profile_id_node = ET.SubElement(xml_root, 'customerProfileId')
        customer_profile_id_node.text = self.customer_profile_id

        billing_info = kwargs.get('billing_info', '')
        credit_card_info= kwargs.get('credit_card_info', '')
        if billing_info or credit_card_info:
            payment_profiles_node = self.create_payment_profile_node('paymentProfile',
                                                                     billing_info,
                                                                     credit_card_info)

            customer_payment_profile_id_node = ET.SubElement(payment_profiles_node, 'customerPaymentProfileId')
            customer_payment_profile_id_node.text = self.customer_payment_profile_id

            xml_root.append(payment_profiles_node)

        return  self.process_request(xml_root)


    def validate(self, **kwargs):
        """
        Test if the last updated payment profile is valid.

        Input fields:
            customer_profile_id
            customer_payment_profile_id
            customer_shipping_address_id - optional
            card_code - optional
            validation_mode

        Output fields:


        """
        if not self.customer_profile_id or not self.customer_payment_profile_id:
            raise AttributeError, _("Missing customer_profile_id or customer_payment_profile_id in input.")

        root_name = 'validateCustomerPaymentProfileRequest'
        xml_root = self.create_base_xml(root_name)
        customer_profile_id_node = ET.SubElement(xml_root, 'customerProfileId')
        customer_profile_id_node.text = self.customer_profile_id

        customer_payment_profile_id_node = ET.SubElement(xml_root, 'customerPaymentProfileId')
        customer_payment_profile_id_node.text = self.customer_payment_profile_id

        customer_shipping_address_id = kwargs.get('customer_shipping_address_id')
        if customer_shipping_address_id:
            customer_shipping_address_id_node = ET.SubElement(xml_root, 'customerShippingAddressId')
            customer_shipping_address_id_node.text = customer_shipping_address_id

        validation_mode = kwargs.get('validation_mode')
        if validation_mode:
            validation_mode_node = ET.SubElement(xml_root, 'validationMode')
            validation_mode_node.text = validation_mode

        return self.process_request(xml_root)


class CIMCustomerProfileTransaction(CIMBase):
    def __init__(self, customer_profile_id, customer_payment_profile_id):
        super(CIMCustomerProfileTransaction, self).__init__()

        self.customer_profile_id = customer_profile_id
        self.customer_payment_profile_id = customer_payment_profile_id


    def create(self, **kwargs):
        """
        Create a payment transaction from an existing customer profile.
        for Authorization and Capture

        Input fields:
            ref_id  - optional
            transaction:
                profile_trans_auth_capture
                amount
                tax
                    amount, name, description
                shipping
                    amount, name, description
                duty
                    amount, name, description
                line_items
                    item_id, name, description, quantity, unit_price, taxable
                customer_profile_id
                customer_payment_profile_id
                customer_shipping_address_id
                returring_billing
                split_tender_id - conditional for partial authorization transaction

         Output fields:
               ref_id
               direct_response

        """
        if not self.customer_profile_id:
            msg_string = "%s Missing customer_profile_id in input." % \
                                'createCustomerProfileTransactionRequest'
            raise AttributeError, _(msg_string)

        root_name = 'createCustomerProfileTransactionRequest'
        xml_root = self.create_base_xml(root_name)

        transaction_node = self.create_transaction_node(**kwargs)
        xml_root.append(transaction_node)

        # extra options
        extra_options_node = ET.SubElement(xml_root, 'extraOptions')
        extra_options_text = '&'.join(['%s=%s' % (x, y) for (x, y) in TRANSACTION_EXTRA_OPTIONS.items()])
        extra_options_node.text = extra_options_text

        return self.process_request(xml_root)



    def create_transaction_node(self, **kwargs):
        amount = kwargs.get('amount', 0)
        if amount <= 0:
            msg_string = '%s - the amount %.2f is not greater than 0.' % \
                               ('<createCustomerProfileTransactionRequest', amount)
            raise ValueError, _(msg_string)
        tax = kwargs.get('tax', '')
        shipping = kwargs.get('shipping')
        line_items_list = kwargs.get('line_items_list')
        customer_shipping_address_id = kwargs.get('customer_shipping_address_id')
        order = kwargs.get('order')
        tax_exempt = kwargs.get('tax_exempt')
        recurring_billing = kwargs.get('recurring_billing')
        card_code = kwargs.get('card_code')
        split_tender_id = kwargs.get('split_tender_id')

        transaction_node = ET.Element("transaction")
        trans_auth_capture_node = ET.SubElement(transaction_node, 'profileTransAuthCapture')


        # amount node
        amount_node = ET.SubElement(trans_auth_capture_node, "amount")
        amount_node.text = str(amount)

        # tax node
        if tax and type(tax) is dict:
            tax = to_camel_case(tax)
            tax_node = ET.SubElement(trans_auth_capture_node, 'tax')
            tax_node = self.build_node_from_dict(tax_node,
                                                 tax,
                                                 TAX_FIELDS)

        # tax node
        if shipping and type(shipping) is dict:
            shipping = to_camel_case(shipping)
            shipping_node = ET.SubElement(trans_auth_capture_node, 'shipping')
            shipping_node = self.build_node_from_dict(shipping_node,
                                                 shipping,
                                                 SHIPPING_FIELDS)

        # line items
        if line_items_list and type(line_items_list) is list:
            for line_items in line_items_list:
                if line_items and type(line_items) is dict:
                    line_items_node = ET.SubElement(trans_auth_capture_node, 'lineItems')
                    line_items_node = self.build_node_from_dict(line_items_node,
                                                                line_items,
                                                                LINE_ITEMS_FIELDS)

        # customer profile id
        customer_profile_id_node = ET.SubElement(trans_auth_capture_node, "customerProfileId")
        customer_profile_id_node.text = self.customer_profile_id

        # customer payment profile id
        customer_payment_profile_id_node = ET.SubElement(trans_auth_capture_node, "customerPaymentProfileId")
        customer_payment_profile_id_node.text = self.customer_payment_profile_id

        # customer shipping address id
        if customer_shipping_address_id:
            customer_shipping_address_id_node = ET.SubElement(trans_auth_capture_node, "customerShippingAddressId")
            customer_shipping_address_id_node.text = customer_shipping_address_id

        # order
        if order and type(order) is dict:
            order = to_camel_case(order)
            order_node = ET.SubElement(trans_auth_capture_node, 'order')
            order_node = self.build_node_from_dict(order_node,
                                                 order,
                                                 ORDER_FIELDS)

        # tax exempt
        if tax_exempt:
            tax_exempt_node = ET.SubElement(trans_auth_capture_node, "taxExempt")
            tax_exempt_node.text = tax_exempt

        # recurring billing
        if recurring_billing:
            recurring_billing_node = ET.SubElement(trans_auth_capture_node, "recurringBilling")
            recurring_billing_node.text = recurring_billing

        # card code
        if card_code:
            card_code_node = ET.SubElement(trans_auth_capture_node, "cardCode")
            card_code_node.text = card_code

        # split tender id
        if split_tender_id:
            split_tender_id_node = ET.SubElement(trans_auth_capture_node, "splitTenderId")
            split_tender_id_node.text = split_tender_id


        return transaction_node


class CIMHostedProfilePage(CIMBase):
    def __init__(self, customer_profile_id):
        super(CIMHostedProfilePage, self).__init__()

        self.customer_profile_id = customer_profile_id

    def get(self, **kwargs):
        """
        Get the token to initiate a request for direct access to the Authorize.Net hosted profile page.

        Input fields:
            customer_profile_id
            hosted_profile_settings - optional
                setting_name
                setting_value

        Output fields:
            token - if not used within 15 minutes of the original API call, this token expires.

        """
        if not self.customer_profile_id:
            msg_string = "%s Missing customer_profile_id in input." % \
                                'getHostedProfilePageRequest'
            raise AttributeError, _(msg_string)

        root_name = 'getHostedProfilePageRequest'
        xml_root = self.create_base_xml(root_name)

        customer_profile_id_node = ET.SubElement(xml_root, 'customerProfileId')
        customer_profile_id_node.text = self.customer_profile_id

        hosted_profile_settings = kwargs.get('hosted_profile_settings')
        if hosted_profile_settings and type(hosted_profile_settings) is dict:
            hosted_profile_settings_node = ET.SubElement(xml_root, 'hostedProfileSettings')
            hosted_profile_settings = to_camel_case(hosted_profile_settings)
            for key in hosted_profile_settings.keys():
                setting_node = ET.SubElement(hosted_profile_settings_node, 'setting')
                hosted_profile_setting = {'settingName': key}
                setting_node = self.build_node_from_dict(setting_node,
                                                         hosted_profile_setting,
                                                         ('settingName', ))
                hosted_profile_setting = {'settingValue': hosted_profile_settings[key]}
                setting_node = self.build_node_from_dict(setting_node,
                                                         hosted_profile_setting,
                                                         ('settingName', 'settingValue'))
        #print ET.tostring(xml_root)
        return self.process_request(xml_root)



class CIMCustomerShippingAddress(CIMBase):
    def __init__(self, customer_profile_id):
        super(CIMCustomerShippingAddress, self).__init__()

        self.customer_profile_id = customer_profile_id


    def create(self, **kwargs):
        pass

    def delete(self, **kwargs):
        pass

    def get(self, **kwargs):
        pass

    def update(self, **kwargs):
        pass


