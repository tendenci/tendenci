from __future__ import print_function
from datetime import datetime
import stripe
from django.conf import settings
from django.core.management.base import BaseCommand
from tendenci.apps.payments.stripe.utils import stripe_set_app_info


class Command(BaseCommand):
    """
    Sync stripe connected accounts - currently, charges
    Stripe API docs: https://stripe.com/docs/api/python#list_charges
    """
    def handle(self, *args, **options):
        from tendenci.apps.payments.stripe.models import StripeAccount, Charge
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_set_app_info(stripe)
        
        stripe_accounts = StripeAccount.objects.filter(status_detail='active')
        for stripe_account in stripe_accounts:
            #The charges are returned in sorted order, with the most recent charges
            #appearing first
            has_more = True
            starting_after = None
            [stop_point] = Charge.objects.filter(account=stripe_account
                                    ).values_list('charge_id', flat=True).order_by('-charge_dt')[:1] or [None]
            
            while has_more:
                if starting_after:
                    stripe_charges = stripe.Charge.list(stripe_account=stripe_account.stripe_user_id,
                                                        starting_after=starting_after)
                else:
                    stripe_charges = stripe.Charge.list(stripe_account=stripe_account.stripe_user_id)
                has_more = stripe_charges.has_more
                for i, stripe_charge in enumerate(stripe_charges):
                    if stop_point and stop_point == stripe_charge.id:
                        has_more = False
                        break
                    starting_after = stripe_charge.id
                    if not Charge.objects.filter(charge_id=stripe_charge.id).exists():
                        params = {'account': stripe_account,
                                  'charge_id': stripe_charge.id,
                                  'amount': stripe_charge.amount/100.0,
                                  'amount_refunded': stripe_charge.amount_refunded/100.0,
                                  'currency': stripe_charge.currency,
                                  'captured': stripe_charge.captured,
                                  'livemode': stripe_charge.livemode,
                                  'charge_dt': datetime.fromtimestamp(stripe_charge.created),
                                  }
                        charge = Charge(**params)
                        charge.save()         
