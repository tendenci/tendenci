from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    This command checks membership entries and confirms
    whether they are blank by setting status_detail to 'empty.'
    """
    def handle(self, *args, **options):
        from memberships.models import AppEntry

        # for every membership entry that is associated with a user
        # check for first name last name and email
        for entry in AppEntry.objects.all(user_set__isnull=False):

            fn = entry.first_name.split()
            ln = entry.last_name.split()
            em = entry.email.split()

            if not all(fn, ln, em):
                print entry.pk, entry.status_detail, 'empty'
