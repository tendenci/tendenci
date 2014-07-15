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
        from tendenci.addons.recurring_payments.models import RecurringPayment
        from tendenci.addons.recurring_payments.utils import run_a_recurring_payment

        verbosity = int(options['verbosity'])
        recurring_payments = RecurringPayment.objects.filter(status_detail='active', status=True)
        for rp in recurring_payments:
            run_a_recurring_payment(rp, verbosity)
