from __future__ import print_function
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    """
    This command creates profiles for users who
    don't have profiles.
    """
    def handle(self, *args, **options):
        from django.contrib.auth.models import User
        from tendenci.apps.profiles.models import Profile

        users = User.objects.all()
        for user in users:
            try:
                profile = user.profile
            except ObjectDoesNotExist:
                profile = Profile.objects.create_profile(user)
                if options['verbosity'] > 1:
                    print(profile)
