
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Sync (state) groups managed by (or tied to) chapter coordinators.

        1) Add chapter members (and national members) from the state to the state group.
        
    Usage: python manage.py sync_chapter_coord_groups --coord_agency_id 1
           python manage.py sync_chapter_coord_groups
    """
    def add_arguments(self, parser):
        parser.add_argument('--coord_agency_id',
            dest='coord_agency_id',
            default=None,
            help='Coordinating agency id')
        
    def sync_type_reps_group(self, group, reps_list, verbosity=1):
        for u in reps_list:
            if not group.members.filter(id=u).exists():
                # this user not in group - add as group member
                group.members.add(u)
                if verbosity >= 2:
                    print(f'Added {u} to group {group}')

    def handle(self, *args, **kwargs):
        from tendenci.apps.profiles.models import Profile
        from tendenci.apps.chapters.models import ChapterMembership, CoordinatingAgency
        
        verbosity = int(kwargs['verbosity'])
        verbosity = 2
        coord_agency_id = kwargs.get('coord_agency_id', None)
        
        coord_agencies = CoordinatingAgency.objects.all()
        if coord_agency_id:
            coord_agencies = coord_agencies.filter(id=coord_agency_id)

        for coord_agency in coord_agencies:
            state = coord_agency.state
            group = coord_agency.group
            
            if state and group:
                if verbosity >= 2:
                    print(f'Processing for state "{state}"')
                chapter_memberships = ChapterMembership.objects.filter(chapter__state=state)
                chapter_memberships = chapter_memberships.exclude(status_detail='archive')
            
                for chapter_membership in chapter_memberships:
                    user = chapter_membership.user
                    if not group.members.filter(id=user.id).exists():
                        group.members.add(user)
                        
                profiles = Profile.objects.filter(state=state)
                for profile in profiles:
                    if profile.member_number:
                        if not group.is_member(profile.user):
                            group.members.add(profile.user)          

        if verbosity >= 2:
            print('Done')
