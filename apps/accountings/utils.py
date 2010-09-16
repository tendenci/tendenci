from accountings.models import Acct, AcctEntry, AcctTran

def make_acct_entries(user, invoice, amount, **kwargs):
    """
        make the actual accounting entries
    """
    ae = AcctEntry.objects.create_acct_entry(user, 'invoice', invoice.id)
    if not invoice.is_tendered:
        make_acct_entries_initial(user, ae, amount)
    else:
        make_acct_entries_closing(user, ae, amount)
        
        if invoice.invoice_object_type == 'make_payment':
            make_acct_entries_general_sale(user, ae, amount, 'make_payment')
        elif invoice.invoice_object_type == 'event_registration':
            make_acct_entries_event_registration(user, ae, amount)
        elif invoice.invoice_object_type == 'job':
            make_acct_entries_job(user, ae, amount)
        elif invoice.invoice_object_type == 'directory':
            make_acct_entries_directory(user, ae, amount)
        elif invoice.invoice_object_type == 'donation':
            make_acct_entries_donation(user, ae, amount)

def make_acct_entries_initial(user, acct_entry, amount, **kwargs):
    """Make the first set of accounting entries when the invoice is tendered
    
        CREDIT unearned revenue (acct 220000)
        DEBIT accouonts receivable (acct 120000)
        
       NOTE - For the purpose of storing the amounts in tendenci, all credits will be
        a negative number.
    """
    # credit to unearned revenue
    acct = Acct.objects.get(account_number=220000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount*(-1))
    
    # debit to accounts receivable
    acct = Acct.objects.get(account_number=120000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount)
    
def make_acct_entries_closing(user, acct_entry, amount, **kwargs):
    """Make the last set of accounting entries when the invoice is receiving payment.
    
        DEBIT Unearned Revenue (L)
        CREDIT Accounts Receviable (A)
        DEBIT Checking or Merchant Account (A)
        CREDIT Sales (L)  ***sales credit is done through the select case in make_acct_entries
        
     NOTE - For the purpose of storing the amounts in tendenci, all credits will be
        a negative number.
    """ 
    # DEBIT to unearned revenue
    acct = Acct.objects.get(account_number=220000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount)
    
    # CREDIT to accounts receivable
    acct = Acct.objects.get(account_number=120000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount*(-1))
    
    # DEBIT CHECKING OR MERCHANT ACCOUNT
    acct = Acct.objects.get(account_number=106000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount)
    
def make_acct_entries_general_sale(user, acct_entry, amount, object_type, **kwargs):
    """
        Payment has now been received and we want to update the accounting
    """
    #CREDIT makepayment SALES
    if object_type =='make_payment': acct_number = 406700
    elif object_type =='donation': acct_number = 405100
    elif object_type =='course': acct_number = 404600
    elif object_type =='directory': acct_number = 404400
    elif object_type =='job': acct_number = 402500
    elif object_type =='resume': acct_number = 403500
    elif object_type =='membership': acct_number = 404700
    else: acct_number = 400100
        
    acct = Acct.objects.get(account_number=acct_number)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount*(-1)) 
    
def make_acct_entries_event_registration(user, acct_entry, amount, **kwargs):
    acct_number = 402000
    #CREDIT event SALES
    acct = Acct.objects.get(account_number=acct_number)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount*(-1)) 

def make_acct_entries_job(user, acct_entry, amount, **kwargs):
    acct_number = 402500
    #CREDIT event SALES
    acct = Acct.objects.get(account_number=acct_number)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount*(-1)) 
    
def make_acct_entries_directory(user, acct_entry, amount, **kwargs):
    acct_number = 404400
    #CREDIT event SALES
    acct = Acct.objects.get(account_number=acct_number)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount*(-1)) 
    
def make_acct_entries_donation(user, acct_entry, amount, **kwargs):
    acct_number = 405100
    #CREDIT event SALES
    acct = Acct.objects.get(account_number=acct_number)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount*(-1)) 
    
    
def make_acct_entries_discount(user, invoice, acct_entry, d, **kwargs):
    """ Payment has now been received and we want to update the accounting entries
    
       ***in this case the original accounting entry is different than the current
        current invoice total - adjust the discount accounts accordingly
    
            DEBIT Discount Account (L) 
            CREDIT Accounts Receviable (A) 
        
       NOTE - For the purpose of storing the amounts in tendenci, all credits will be
        a negative number.
    """
    myamount = d['original_invoice_total'] - invoice.total
    
    if d['original_invoice_balance'] <= 0:
        # the invoice has been paid and we need to adjust the specific account
        discount_number = d['discount_account_number']
        reverse_sale = True
    else:
        discount_number = '220000'  #   unearned revenue
        reverse_sale = False
        
    #  DEBIT DISCOUNT ACCOUNT  
    acct = Acct.objects.get(account_number=discount_number)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, myamount)    
    
    # CREDIT ACCOUNTS RECEIVABLE    
    acct = Acct.objects.get(account_number=120000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, myamount*(-1))
    
    if reverse_sale:
        # DEBIT ACCOUNTS RECEIVABLE
        acct = Acct.objects.get(account_number=120000)
        AcctTran.objects.create_acct_tran(user, acct_entry, acct, myamount) 
        
        # CREDIT CHECKING
        acct = Acct.objects.get(account_number=106000)
        AcctTran.objects.create_acct_tran(user, acct_entry, acct, myamount*(-1))
      
    
    
    
    