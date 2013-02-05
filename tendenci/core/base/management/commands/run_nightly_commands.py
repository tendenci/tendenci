from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    """
    Run a series of commands that should be run on a
    nightly (daily) basis.
    """
    def handle(self, *args, **options):
        call_command('collect_metrics')
        call_command('expire_jobs')
        call_command('expire_resumes')
        call_command('expire_stories')
        call_command('send_event_reminders')
        call_command('clean_corporate_memberships')
        call_command('send_membership_notices')
        call_command('clean_memberships')
        call_command('refresh_membership_groups')
