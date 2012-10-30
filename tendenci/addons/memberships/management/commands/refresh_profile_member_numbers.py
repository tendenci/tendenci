from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Populate the member IDs (or member numbers) to profiles.
    """
    def handle(self, *args, **options):
        from tendenci.apps.profiles.models import Profile
        verbosity = int(options['verbosity'])

        for profile in Profile.objects.all():
            member_number = profile.refresh_member_number()

            if verbosity:
                print 'profile(%d) has member number %s' % \
                    (profile.pk, member_number)
