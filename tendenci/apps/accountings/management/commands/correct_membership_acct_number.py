from __future__ import print_function
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    """
    Correct the account_number of AcctTran records for the memberships
    for those that are wrongly assigned with the event's account_number.

    Usage: python manage.py correct_membership_acct_number
    """

    def handle(self, *args, **options):
        from tendenci.apps.memberships.models import MembershipDefault
        from tendenci.apps.invoices.models import Invoice
        from tendenci.apps.accountings.models import Acct, AcctEntry

        account_number = MembershipDefault().get_acct_number()
        acct = Acct.objects.get(account_number=account_number)

        accts_ignore = Acct.objects.filter(
                            account_number__in=['220000',
                                                '120000',
                                                '106000']
                                )
        num_trans_updated = 0

        [content_type] = ContentType.objects.filter(
                                        app_label='memberships',
                                        model='membershipdefault'
                                        )[:1] or [None]
        if content_type:
            membership_invoices = Invoice.objects.filter(
                                object_type=content_type
                                )
            for invoice in membership_invoices:
                acct_entries = AcctEntry.objects.filter(
                                source='invoice',
                                object_id=invoice.id)
                for ae in acct_entries:
                    acct_trans = ae.trans.exclude(
                                    account=acct).exclude(
                                    account__in=accts_ignore)
                    if acct_trans.exists():
                        num_trans_updated += acct_trans.count()
                        acct_trans.update(account=acct)

        print('# acct_tran updated ', num_trans_updated)
