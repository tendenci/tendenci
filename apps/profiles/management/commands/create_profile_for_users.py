from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    This command creates profiles for userse who
    don't have profiles.
    """
    def handle(self, *args, **options):
        from django.contrib.auth.models import User
        from profiles.models import Profile

        users = User.objects.all()
        for user in users:

            profile = user.get_profile()
            if not profile:
                profile = Profile.objects.create_profile(user)

            if options['verbosity'] > 1:
                print profile
