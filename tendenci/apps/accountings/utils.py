from tendenci.apps.accountings.models import Acct, AcctEntry, AcctTran


def make_acct_entries(user, invoice, amount, **kwargs):
    """
        make the actual accounting entries
    """
    obj = invoice.get_object()
    if obj and hasattr(obj, 'make_acct_entries'):
        obj.make_acct_entries(user, invoice, amount)
    else:
        ae = AcctEntry.objects.create_acct_entry(user, 'invoice', invoice.id)
        if not invoice.is_tendered:
            make_acct_entries_initial(user, ae, amount)
        else:
            make_acct_entries_closing(user, ae, amount)

            #CREDIT SALES
            make_acct_entries_sale(user, obj, ae, amount)


def make_acct_entries_initial(user, acct_entry, amount, **kwargs):
    """Make the first set of accounting entries when the invoice is tendered

        CREDIT unearned revenue (acct 220000)
        DEBIT accouonts receivable (acct 120000)

       NOTE - For the purpose of storing the amounts in tendenci,
       all credits will be a negative number.
    """
    # credit to unearned revenue
    acct = Acct.objects.get(account_number=220000)
    AcctTran.objects.create_acct_tran(user,
                                      acct_entry,
                                       acct,
                                       amount * (-1))

    # debit to accounts receivable
    acct = Acct.objects.get(account_number=120000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount)


def make_acct_entries_closing(user, acct_entry, amount, **kwargs):
    """Make the last set of accounting entries when the invoice
        is receiving payment.

        DEBIT Unearned Revenue (L)
        CREDIT Accounts Receviable (A)
        DEBIT Checking or Merchant Account (A)
        CREDIT Sales (L)  ***sales credit is done through the
            select case in make_acct_entries

     NOTE - For the purpose of storing the amounts in tendenci,
         all credits will be a negative number.
    """
    # DEBIT to unearned revenue
    acct = Acct.objects.get(account_number=220000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount)

    # CREDIT to accounts receivable
    acct = Acct.objects.get(account_number=120000)
    AcctTran.objects.create_acct_tran(user,
                                      acct_entry,
                                      acct,
                                      amount * (-1))

    # DEBIT CHECKING OR MERCHANT ACCOUNT
    acct = Acct.objects.get(account_number=106000)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, amount)


def make_acct_entries_sale(user, obj, acct_entry, amount, **kwargs):
    """
        Payment has now been received and we want to update the accounting
    """
    #CREDIT SALES
    acct_number = ''
    if obj and hasattr(obj, 'get_acct_number'):
        acct_number = obj.get_acct_number
        if not Acct.objects.filter(account_number=acct_number).exists():
            acct_number = ''

    if not acct_number:
        # general sale
        acct_number = 400100

    acct = Acct.objects.get(account_number=acct_number)

    AcctTran.objects.create_acct_tran(user,
                                      acct_entry,
                                      acct,
                                      amount * (-1))


def make_acct_entries_discount(user, invoice, acct_entry, d, **kwargs):
    """ Payment has now been received and we want to update
         the accounting entries

       ***in this case the original accounting entry is different
          than the current current invoice total - adjust the
          discount accounts accordingly

            DEBIT Discount Account (L)
            CREDIT Accounts Receviable (A)

       NOTE - For the purpose of storing the amounts in tendenci,
       all credits will be a negative number.
    """
    myamount = d['original_invoice_total'] - invoice.total

    if d['original_invoice_balance'] <= 0:
        # the invoice has been paid and we need to adjust the specific account
        discount_number = d['discount_account_number']
        reverse_sale = True
    else:
        discount_number = '220000'  # unearned revenue
        reverse_sale = False

    #  DEBIT DISCOUNT ACCOUNT
    acct = Acct.objects.get(account_number=discount_number)
    AcctTran.objects.create_acct_tran(user, acct_entry, acct, myamount)

    # CREDIT ACCOUNTS RECEIVABLE
    acct = Acct.objects.get(account_number=120000)
    AcctTran.objects.create_acct_tran(user,
                                      acct_entry,
                                      acct,
                                      myamount * (-1))

    if reverse_sale:
        # DEBIT ACCOUNTS RECEIVABLE
        acct = Acct.objects.get(account_number=120000)
        AcctTran.objects.create_acct_tran(user, acct_entry, acct, myamount)

        # CREDIT CHECKING
        acct = Acct.objects.get(account_number=106000)
        AcctTran.objects.create_acct_tran(user,
                                          acct_entry,
                                          acct,
                                          myamount * (-1))


def make_acct_entries_reversing(user, invoice, amount, **kwargs):
    """
        Make accounting transactions for the void payment.

        CREDIT to unearned revenue
        DEBIT to accounts receivables
        CREDIT to checking or merchant account
        DEBIT to void payment
    """
    obj = invoice.get_object()
    if obj and hasattr(obj, 'make_acct_entries_reversing'):
        obj.make_acct_entries_reversing(user, invoice, amount)
    else:
        [ae] = AcctEntry.objects.filter(source='invoice',
                                      object_id=invoice.id,
                                      status=True)[:1] or [None]
        if ae:
            make_acct_entries_closing_reversing(user,
                                                ae,
                                                amount,
                                                **kwargs)
            make_acct_entries_sale_reversing(user,
                                             obj,
                                             ae,
                                             amount,
                                             **kwargs)


def make_acct_entries_closing_reversing(user, acct_entry, amount, **kwargs):
    """Make the last set of accounting entries when the invoice
        is receiving payment.

        DEBIT Unearned Revenue (L)
        CREDIT Accounts Receviable (A)
        DEBIT Checking or Merchant Account (A)
        CREDIT Sales (L)  ***sales credit is done through the
            select case in make_acct_entries

     NOTE - For the purpose of storing the amounts in tendenci,
         all credits will be a negative number.
    """
    # CREDIT to unearned revenue
    acct = Acct.objects.get(account_number=220000)
    AcctTran.objects.create_acct_tran(user,
                                      acct_entry,
                                      acct,
                                      amount * (-1))

    # DEBIT to accounts receivable
    acct = Acct.objects.get(account_number=120000)
    AcctTran.objects.create_acct_tran(user,
                                      acct_entry,
                                      acct,
                                      amount)

    # CREDIT CHECKING OR MERCHANT ACCOUNT
    acct = Acct.objects.get(account_number=106000)
    AcctTran.objects.create_acct_tran(user,
                                      acct_entry,
                                      acct,
                                      amount * (-1))


def make_acct_entries_sale_reversing(user,
                                     obj,
                                     acct_entry,
                                     amount,
                                     **kwargs):
    """
        Payment has now been void and we want to update the accounting
    """
    # DEBIT SALES
    acct_number = ''
    if obj and hasattr(obj, 'get_acct_number'):
        acct_number = obj.get_acct_number
        if not Acct.objects.filter(account_number=acct_number).exists():
            acct_number = ''

    if not acct_number:
        # general sale
        acct_number = 400100

    acct = Acct.objects.get(account_number=acct_number)

    AcctTran.objects.create_acct_tran(user,
                                      acct_entry,
                                      acct,
                                      amount)
