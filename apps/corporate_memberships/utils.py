import os
from django.conf import settings
from django.utils import simplejson
from site_settings.utils import get_setting
from perms.utils import is_admin

# get the corpapp default fields list from json
def get_corpapp_default_fields_list():
    json_fields_path = os.path.join(settings.PROJECT_ROOT, 
                                    "templates/corporate_memberships/regular_fields.json")
    fd = open(json_fields_path, 'r')
    data = ''.join(fd.read())
    fd.close()
    
    if data:
        return simplejson.loads(data)
    return None

def get_corporate_membership_type_choices(user, corpapp):
    cmt_list = []
    corporate_membership_types = corpapp.corp_memb_type.all()
    currency_symbol = get_setting("site", "global", "currencysymbol")
    
    for cmt in corporate_membership_types:
        print cmt.price
        cmt_list.append((cmt.id, '%s - %s%0.2f' % (cmt.name, currency_symbol, cmt.price)))
        
    return cmt_list        
   
def get_payment_method_choices(user):
    if is_admin(user):
        return (('paid - check', 'User paid by check'),
                ('paid - cc', 'User paid by credit card'),
                ('Credit Card', 'Make online payment NOW'),)
    else:
        return (('check', 'Check'),
                ('cash', 'Cash'),
                ('cc', 'Credit Card'),)
    