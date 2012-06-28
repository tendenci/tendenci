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

        memberships = Membership.objects.filter(
            status=1,
            status_detail='active',
            expire_dt__gt=datetime.now(),
            corporate_membership_id__gt=0
        )

        for membership in memberships:
            corporate = CorporateMembership.objects.filter(pk=membership.corporate_membership_id)
            membership.expire_dt = corporate.expiration_dt
            membership.save()
