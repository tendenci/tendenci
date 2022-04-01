from logging import getLogger
import traceback

#import traceback
from django.core.management.base import BaseCommand
from django.urls import reverse
#from django.template.loader import render_to_string
#from django.template import TemplateDoesNotExist
from django.conf import settings
from tendenci.apps.site_settings.utils import get_setting


def _verify_settings(*args):
    return all([getattr(settings, setting, '') for setting in args])

def _check_stripe():
    return _verify_settings('STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY')

def _check_square():
    return _verify_settings('SQUARE_APPLICATION_ID', 'SQUARE_ACCESS_TOKEN', 'SQUARE_LOCATION_ID')

def _check_authorize_net():
    return _verify_settings('MERCHANT_LOGIN', 'MERCHANT_TXN_KEY')

def has_supported_merchant_account(platform):
    if platform == 'authorizenet':
        return _check_authorize_net()
    elif platform == 'stripe':
        return _check_stripe()
    elif platform == 'square':
        return _check_square()


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
        from tendenci.apps.recurring_payments.models import RecurringPayment
        from tendenci.apps.recurring_payments.utils import run_a_recurring_payment
        logger = getLogger('run_recurring_payment')

        if get_setting('module', 'recurring_payments', 'enabled'):
            verbosity = int(options['verbosity'])
            recurring_payments = RecurringPayment.objects.filter(status_detail='active', status=True)
            for rp in recurring_payments:
                if has_supported_merchant_account(rp.platform):
                    try:
                        run_a_recurring_payment(rp, verbosity)
                    except:
                        print(traceback.format_exc())
                        rp_url = '%s%s' % (get_setting('site', 'global', 'siteurl'),
                                        reverse('recurring_payment.view_account', args=[rp.id]))
                        logger.error(f'Error processing recurring payment {rp_url}...\n\n{traceback.format_exc()}')
        else:
            print('Recurring payments not enabled')
