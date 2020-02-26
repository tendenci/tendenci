
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Update the expiration date of memberships
    user the expiration of it's corporate membership.
    """
    def handle(self, **options):
        from django.core.exceptions import ObjectDoesNotExist
        from tendenci.apps.corporate_memberships.models import CorpMembership
        from tendenci.apps.memberships.models import MembershipDefault
        verbosity = int(options['verbosity'])

        corporates = CorpMembership.objects.filter(status=True, status_detail='active')

        for corporate in corporates:
            memberships = MembershipDefault.objects.filter(
                corporate_membership_id=corporate.pk
            )

            for membership in memberships:
                membership.status = corporate.status
                membership.status_detail = corporate.status_detail
                membership.expire_dt = corporate.expiration_dt
                membership.save()

                try:
                    membership.user.profile.refresh_member_number()
                except ObjectDoesNotExist:
                    pass

                if verbosity:
                    print(membership)
