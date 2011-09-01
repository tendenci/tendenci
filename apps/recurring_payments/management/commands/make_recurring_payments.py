from datetime import datetime, timedelta
import time
import traceback
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist


class Command(BaseCommand):
    """
    make_recurring_payments
    
    This script does the following:
        1) check and populate payment profile for each recurring payment entry.
        2) generate invoice(s) for recurring payments if needed.
        3) make payment transactions for invoice(s) upon due date.
        4) notify admin for each transaction.
    
    Usage: ./manage.py make_recurring_payments --verbosity 1
    """
    
    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']
            
        from recurring_payments.models import (RecurringPayment,
                                               RecurringPaymentInvoice,
                                               PaymentProfile,
                                               PaymentTransaction)
        from recurring_payments.authnet.cim import CIMCustomerProfile
        from emails.models import Email
        from site_settings.utils import get_setting
        from recurring_payments.utils import RecurringPaymentEmailNotices
        rp_email_notice = RecurringPaymentEmailNotices()
        
        
        recurring_payments = RecurringPayment.objects.filter(status_detail='active', status=1)
        now = datetime.now()
        
        for rp in recurring_payments:
            # check and store payment profiles in local db
            if verbosity > 1:
                print
                print 'Processing for "%s":' % rp
                print
                print '\tPopulating payment profiles from payment gateway...'
            rp.populate_payment_profile()
            
            # create invoices if needed
            if verbosity > 1:
                print '\tChecking and generating invoice(s)  ...' 
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
                            status_detail='active')
                
                if payment_profiles:
            
                    for rp_invoice in rp_invoices:
                        # make payment transaction and then update recurring_payment fields
                        if verbosity > 1:
                            print '\tMaking payment transaction for recurring payment (%s) - amount: %.2f ...' \
                                    % (rp, rp_invoice.invoice.balance)
                         
                        success = False    
                        for payment_profile in payment_profiles:
                            payment_profile_id = payment_profile.payment_profile_id
                            payment_transaction = rp_invoice.make_payment_transaction(payment_profile_id)
                            if payment_transaction.status:
                                success = True
                                break
                            else:
                                # so this is an invalid payment profile
                                # update the status detail so we won't use it next time
                                payment_profile.status_detail = 'invalid'
                                payment_profile.save()
                        
                        if success:
                            rp.last_payment_received_dt = now
                            rp_invoice.payment_received_dt = now
                            rp_invoice.save()
                            rp.num_billing_cycle_completed += 1
                            print '\tSuccess.'
                        else:
                            rp.num_billing_cycle_failed += 1
                            print '\tFailed  - \n\t code - %s \n\t text - %s' \
                                                % (payment_transaction.message_code,
                                                   payment_transaction.message_text)
                            
                        # send out email notifications - for both successful and failed transactions
                        # to admin
                        rp_email_notice.email_admins_transaction_result(payment_transaction)
                        # to customer
                        rp_email_notice.email_customer_transaction_result(payment_transaction)
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
                    
                
                
            
                
            