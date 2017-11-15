from __future__ import print_function
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Make corporate_membership_id and corp_profile_id consistent for memberships 
    """
    def handle(self, *args, **kwargs):
        from tendenci.apps.corporate_memberships.models import CorpMembership
        from tendenci.apps.memberships.models import MembershipDefault

        for corp_memb in CorpMembership.objects.all().exclude(status_detail='archive'):
            memberships = MembershipDefault.objects.filter(corporate_membership_id=corp_memb.id)
            for m in memberships:
                if m.corp_profile_id != corp_memb.corp_profile.id:
                    old_corp_profile_id = m.corp_profile_id
                    m.corp_profile_id = corp_memb.corp_profile.id
                    print(m.id, '- changed corp_profile_id from %s to %s' % (old_corp_profile_id, corp_memb.corp_profile.id))
                    m.save()
