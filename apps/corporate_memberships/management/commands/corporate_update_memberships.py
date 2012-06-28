from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Update the expiration date of memberships
    user the expiration of it's corporate membership.
    """
    def handle(self, *args, **kwargs):
        from corporate_memberships.models import CorporateMembership
        from memberships.models import Membership

        corporates = CorporateMembership.objects.all()

        for corporate in corporates:
            memberships = Membership.objects.filter(
                corporate_membership_id=corporate.pk
            )

            for membership in memberships:
                membership.status = corporate.status
                membership.status_detail = corporate.status_detail
                membership.expire_dt = corporate.expiration_dt
                membership.user.profile.refresh_member_number()
                membership.save()
