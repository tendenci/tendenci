
def get_account_number(invoice, d):
    discount_account = ''
    overage_account = ''
    if invoice.invoice_object_type == 'event_registration':
        discount_account = '462000'
        overage_account = '402000'
    elif invoice.invoice_object_type == 'catalog_cart':
        discount_account = '463700'
        overage_account = '403700'
    elif invoice.invoice_object_type == 'directory':
        discount_account = '464400'
        overage_account = '404400'
    elif invoice.invoice_object_type == 'donation':
        discount_account = '465100'
        overage_account = '405100'
    elif invoice.invoice_object_type == 'make_payment':
        discount_account = '466700'
        overage_account = '406700'
    elif invoice.invoice_object_type == 'job':
        discount_account = '462500'
        overage_account = '402500'
    else:
        discount_account = '460100'
        overage_account = '400100'
        
    if d.get('discount', '') <> '': return discount_account
    if d.get('overage', '') <> '': return overage_account
    
        