from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Clean up the expired corporate memberships.
        1) Set the status_detail to expired
        2) Clean up the individual memberships under this corporate.

    Usage: python manage.py clean_corporate_memberships
    """
    def handle(self, *args, **kwargs):
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from tendenci.apps.corporate_memberships.models import (
                            CorpMembership, CorporateMembershipType)
        from tendenci.apps.memberships.models import MembershipDefault

        [admin] = User.objects.filter(is_superuser=True).order_by('id')[:1] or [None]
        for corp_membership_type in CorporateMembershipType.objects.all():
            membership_type = corp_membership_type.membership_type
            grace_period = membership_type.expiration_grace_period
            date_to_expire = datetime.now() - relativedelta(days=grace_period)

            corp_memberships = CorpMembership.objects.filter(
                corporate_membership_type=corp_membership_type,
                expiration_dt__lt=date_to_expire,
                status_detail='active',
                status=True)
            for corp_membership in corp_memberships:
                corp_membership.status_detail = 'expired'
                corp_membership.save()

                # individual memberships under this corporate
                memberships = MembershipDefault.objects.filter(
                            corporate_membership_id=corp_membership.id
                                )
                for membership in memberships:
                    membership.expire(admin)
