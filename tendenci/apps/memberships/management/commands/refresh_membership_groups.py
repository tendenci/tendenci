from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Loop through users/membership-types
    and add or remove the user from the group.
    """
    def handle(self, *args, **kwargs):
        from tendenci.apps.memberships.models import MembershipDefault
        MembershipDefault.refresh_groups()
