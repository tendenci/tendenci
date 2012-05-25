from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Populate the member IDs (or member numbers) to profiles.
    """
    def handle(self, *args, **options):
        from memberships.models import Membership
        
        verbosity = int(options['verbosity'])
 
        memberships = Membership.objects.filter(
            status=1,
            status_detail='active'
        )

        for membership in memberships:
            membership.populate_user_member_id(verbosity=verbosity)