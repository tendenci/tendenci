from datetime import datetime
import time
#import traceback
from django.core.management.base import BaseCommand
#from django.template.loader import render_to_string
#from django.template import TemplateDoesNotExist

UNSUCCESSFUL_TRANS_CODE = ['E00027']

class Command(BaseCommand):
    """
    Make recurring payment transactions.
    
    This script does the following:
        1) check and populate payment profile for each recurring payment entry.
        2) generate invoice(s) for recurring payments if needed.
        3) make payment transactions for invoice(s) upon due date.
        4) notify admins and customers for after each transaction.
    
    Usage: ./manage.py make_recurring_payment_transactions --verbosity 2
    """
    
    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']
        try:
            verbosity = int(verbosity)
        except:
            pass
            
        from recurring_payments.models import (RecurringPayment,
                                               RecurringPaymentInvoice,
                                               PaymentProfile)
        from site_settings.utils import get_setting
        from recurring_payments.utils import RecurringPaymentEmailNotices
        rp_email_notice = RecurringPaymentEmailNotices()
        
        
        recurring_payments = RecurringPayment.objects.filter(status_detail='active', status=1)
        now = datetime.now()
        currency_symbol = get_setting('site', 'global', 'currencysymbol')
        
        for rp in recurring_payments:
            # check and store payment profiles in local db
            if verbosity > 1:
                print
                print 'Processing for "%s":' % rp
                print '...Populating payment profiles from payment gateway...'
            rp.populate_payment_profile()
            
            # create invoices if needed
            if verbosity > 1:
                print '...Checking and generating invoice(s)  ...' 
            rp.check_and_generate_invoices()

            # look for unpaid invoices with current due date or pass due date
            rp_invoices = RecurringPaymentInvoice.objects.filter(
                                                 recurring_payment=rp, 
                                                 invoice__balance__gt=0,
                                                 billing_dt__lte=now
                                                 ).order_by('billing_cycle_start_dt')

                                                 
            if rp_invoices:
                payment_profiles = PaymentProfile.objects.filter(
                            recurring_payment=rp,
                            status=1,
                            status_detail='active'
                            ).order_by('-update_dt')
                
                if payment_profiles:
            
                    for i, rp_invoice in enumerate(rp_invoices):
                        # wait for 3 minutes (duplicate transaction window is 2 minutes) if this is not the first invoice,
                        # otherwise, the payment gateway would through the "duplicate transaction" error.
                        if i > 0: time.sleep(3*60)
                        
                        payment_profile = payment_profiles[0]
                        if rp_invoice.last_payment_failed_dt and \
                            rp_invoice.last_payment_failed_dt > payment_profile.update_dt:
                            # this invoice was processed but failed, and they haven't update the payment profile yet,
                            # so just skip it for now.
                            # only skip if the error code is: E00027 - the transaction was unsuccessful
                            last_error_code = rp_invoice.get_last_transaction_error_code()
                            if last_error_code and last_error_code in UNSUCCESSFUL_TRANS_CODE:
                                continue
                        
                        # make payment transaction and then update recurring_payment fields
                        if verbosity > 1:
                            print '...Making payment transaction for billing cycle (%s -%s) - amount: %s%.2f ...' \
                                    % (rp_invoice.billing_cycle_start_dt.strftime('%m-%d-%Y'),
                                       rp_invoice.billing_cycle_end_dt.strftime('%m-%d-%Y'),
                                       currency_symbol, 
                                       rp_invoice.invoice.balance)
                         
                        success = False    
                        
                        payment_profile_id = payment_profile.payment_profile_id
                        payment_transaction = rp_invoice.make_payment_transaction(payment_profile_id)
                        if payment_transaction.status:
                            success = True
                        
                        
                        if success:
                            rp.last_payment_received_dt = now
                            rp_invoice.payment_received_dt = now
                            rp_invoice.save()
                            rp.num_billing_cycle_completed += 1
                            print '...Success.'
                        else:
                            rp.num_billing_cycle_failed += 1
                            print '...Failed  - \n\t code - %s \n\t text - %s' \
                                                % (payment_transaction.message_code,
                                                   payment_transaction.message_text)
                            
                        # send out email notifications - for both successful and failed transactions
                        # to admin
                        rp_email_notice.email_admins_transaction_result(payment_transaction)
                        # to customer
                        if payment_transaction.message_code not in UNSUCCESSFUL_TRANS_CODE:
                            rp_email_notice.email_customer_transaction_result(payment_transaction)
                        else:
                            # the payment gateway is probably not configured correctly
                            # email to tendenci script support 
                            rp_email_notice.email_script_support_transaction_error(payment_transaction)
                else:
                    # email admin - payment profile not set up
                    # to admin
                    rp_email_notice.email_admins_no_payment_profile(rp)
                    # to customer
                    rp_email_notice.email_customer_no_payment_profile(rp)
                    
                        
                            
            
            # calculate the balance by checking for unpaid invoices       
            rp.balance = rp.get_current_balance()
            rp.outstanding_balance = rp.get_outstanding_balance()
            rp.save()
                    
                
                
            
                
            