from __future__ import print_function
from datetime import datetime
import square
from django.conf import settings
from django.core.management.base import BaseCommand
from tendenci.apps.payments.square.utils import square_set_app_info


class Command(BaseCommand):
    """
    Sync square connected accounts - currently, charges
    Square API docs: https://stripe.com/docs/api/python#list_charges
    """
    def handle(self, *args, **options):
        from tendenci.apps.payments.square.models import SquareAccount, Charge
        
        square.api_key = settings.STRIPE_SECRET_KEY
        square_set_app_info(square)
        
        square_accounts = SquareAccount.objects.filter(status_detail='active')
        for square_account in square_accounts:
            #The charges are returned in sorted order, with the most recent charges
            #appearing first
            has_more = True
            starting_after = None
            [stop_point] = Charge.objects.filter(account=square_account
                                    ).values_list('charge_id', flat=True).order_by('-charge_dt')[:1] or [None]
            
            while has_more:
                if starting_after:
                    square_charges = square.Charge.list(square_account=square_account.square_user_id,
                                                        starting_after=starting_after)
                else:
                    square_charges = square.Charge.list(square_account=square_account.square_user_id)
                has_more = square_charges.has_more
                for i, square_charge in enumerate(square_charges):
                    if stop_point and stop_point == square_charge.id:
                        has_more = False
                        break
                    starting_after = square_charge.id
                    if not Charge.objects.filter(charge_id=square_charge.id).exists():
                        params = {'account': square_account,
                                  'charge_id': square_charge.id,
                                  'amount': square_charge.amount/100.0,
                                  'amount_refunded': square_charge.amount_refunded/100.0,
                                  'currency': square_charge.currency,
                                  'captured': square_charge.captured,
                                  'livemode': square_charge.livemode,
                                  'charge_dt': datetime.fromtimestamp(square_charge.created),
                                  }
                        charge = Charge(**params)
                        charge.save()         
