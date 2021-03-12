
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Sync corporate membership representatives groups for each corp membership type
    or for the corp membership type passed in.

        1) Remove users from the reps groups if they're no longer reps for the pending or active corporate memberships.
        2) Add corp reps to their corresponding groups - pending_group or active_group
        
    Usage: python manage.py sync_corp_reps_groups --corp_mem_type_id 1
           python manage.py sync_corp_reps_groups
    """
    def add_arguments(self, parser):
        parser.add_argument('--corp_mem_type_id',
            dest='corp_mem_type_id',
            default=None,
            help='Corporate membership type id')
        
    def sync_type_reps_group(self, group, reps_list, verbosity=1):
        reps_list = set(reps_list)
        for u in group.members.all():
            if u not in reps_list:
                # this user is in the group but not a rep - remove from the group
                group.members.remove(u)
                if verbosity >= 2:
                    print(f'Removed {u} from group {group}')
        for u in reps_list:
            if not group.members.filter(id=u).exists():
                # this user not in group - add as group member
                group.members.add(u)
                if verbosity >= 2:
                    print(f'Added {u} to group {group}')

    def handle(self, *args, **kwargs):
        from tendenci.apps.corporate_memberships.models import CorpMembership, CorporateMembershipType, CorpMembershipRep
        
        verbosity = int(kwargs['verbosity'])
        verbosity = 2
        corp_mem_type_id = kwargs.get('corp_mem_type_id', None)

        corp_types = CorporateMembershipType.objects.all()
        if corp_mem_type_id:
            corp_types = corp_types.filter(id=corp_mem_type_id)
            
        for corp_type in corp_types:
            if verbosity >= 2:
                print('Syncing groups for corporate membership type: ', corp_type)
            # Sync for pending group
            pending_group = corp_type.pending_group
            if pending_group:
                if verbosity >= 2:
                    print('Syncing pending group: ', pending_group)
                pending_corp_profiles_list = CorpMembership.objects.filter(
                                            corporate_membership_type=corp_type,
                                            status_detail__icontains='pending'
                                            ).values_list('corp_profile', flat=True)
                # list pending reps - users
                pending_reps_list = CorpMembershipRep.objects.filter(corp_profile__in=pending_corp_profiles_list
                                                                     ).values_list('user', flat=True)
                self.sync_type_reps_group(pending_group, pending_reps_list, verbosity=verbosity)
            
            # Sync for active group
            active_group = corp_type.active_group
            if active_group:
                if verbosity >= 2:
                    print('Syncing active group: ', active_group)
                active_corp_profiles_list = CorpMembership.objects.filter(
                                            corporate_membership_type=corp_type,
                                            status_detail='active'
                                            ).values_list('corp_profile', flat=True)
                # list active reps - users
                active_reps_list = CorpMembershipRep.objects.filter(corp_profile__in=active_corp_profiles_list
                                                                     ).values_list('user', flat=True)
                self.sync_type_reps_group(active_group, active_reps_list, verbosity=verbosity)

        if verbosity >= 2:
            print('Done')
