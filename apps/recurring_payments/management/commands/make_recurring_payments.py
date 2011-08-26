from datetime import datetime, timedelta
import time
import traceback
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Get a list of membership notices from the notice table,
    and send each notice to members who meet the criteria. 
    
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
        
        recurring_payments = RecurringPayment.objects.filter(status_detail='active', status=1)
        now = datetime.now()
        
        for rp in recurring_payments:
            # check and store some payment profile info locally
            rp.populate_payment_profile()
            
            # create invoices if needed
                    
            
            # look for unpaid invoices
            rp_invoices = RecurringPaymentInvoice.objects.filter(
                                                 recurring_payment=rp, 
                                                 invoice__balance__gt=0,
                                                 billing_cycle_start_dt__lte=now
                                                 ).order_by('billing_cycle_start_dt')
            
            for rp_invoice in rp_invoices:
                # make payment transaction and then update recurring_payment fields
                success, response_d = rp_invoice.make_payment_transaction()
                
                rp_invoice.billing_dt = now
                rp_invoice.save()
                
                if success:
                    rp.last_payment_received_dt = now
                    rp.num_billing_cycle_completed += 1
                else:
                    rp.num_billing_cycle_failed += 1
                    # failed_reason
                    #rp.failed_reason = response_d['']
                    #rp.current_balance += rp_invoice.invoice.balance
                    #rp.outstanding_balance += rp_invoice.invoice.balance
            
                
            