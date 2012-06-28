from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Update the expiration date of memberships
    user the expiration of it's corporate membership.
    """
    def handle(self, *args, **kwargs):
        from datetime import datetime
        from corporate_memberships.models import CorporateMembership
        from memberships.models import Membership

        corporates = CorporateMembership.objects.filter(
            status=1,
            status_detail='active',
            expiration_dt__gt=datetime.now()
        )

        for corporate in corporates:
            memberships = Membership.objects.filter(
                corporate_membership_id=corporate.pk
            )

            for membership in memberships:
                membership.status = 'active'
                membership.expire_dt = corporate.expiration_dt
                membership.save()
