#import traceback
from django.core.management.base import BaseCommand
#from django.template.loader import render_to_string
#from django.template import TemplateDoesNotExist


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
            
        from recurring_payments.models import RecurringPayment 
        from recurring_payments.utils import run_a_recurring_payment
     
        recurring_payments = RecurringPayment.objects.filter(status_detail='active', status=1)    
        
        for rp in recurring_payments:
            run_a_recurring_payment(rp, verbosity)