from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Set the status detail of the membership to expired.
    Remove the user from the [privileged] group.
    example: python manage.py remove_expired_memberships
    """
    def handle(self, *args, **kwargs):
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from tendenci.apps.memberships.models import Membership, MembershipType
        from tendenci.apps.user_groups.models import GroupMembership

        for membership_type in MembershipType.objects.all():
            grace_period = membership_type.expiration_grace_period

            # get expired memberships out of grace period
            # we can't move the expiration date, but we can
            # move todays day back.
            memberships = Membership.objects.active(
                membership_type=membership_type,
                expire_dt__lt=datetime.now() - relativedelta(days=grace_period)
            )

            for membership in memberships:
                # update profile
                membership.user.profile.refresh_member_number()

                # remove from group
                GroupMembership.objects.filter(
                    member=membership.user,
                    group=membership.membership_type.group
                ).delete()
