
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Refresh object permissions for all corporate memberships
    """
    def handle(self, *args, **kwargs):
        from tendenci.apps.corporate_memberships.models import CorpMembership
        from tendenci.apps.corporate_memberships.utils import corp_membership_update_perms

        for corp_memb in CorpMembership.objects.all().exclude(status_detail='archive'):
            corp_membership_update_perms(corp_memb)

