import subprocess

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    """
    Run a series of commands that should be run on a
    nightly (daily) basis.
    """
    def handle(self, *args, **options):
        from tendenci.core.site_settings.utils import get_setting

        call_command('expire_jobs')
        call_command('expire_resumes')
        call_command('expire_stories')
        call_command('send_event_reminders')
        call_command('clean_corporate_memberships')
        call_command('send_membership_notices')
        call_command('clean_memberships')
        call_command('refresh_membership_groups')
        call_command('send_corp_membership_notices')
        call_command('clean_old_exports')
        call_command('delete_soft_deleted_items')

        # Use Popen for longrunning tasks with heavy queries.
        subprocess.Popen(['python', 'manage.py', 'update_dashboard_stats'])
        subprocess.Popen(['python', 'manage.py', 'collect_metrics'])

        if all([get_setting('module', 'recurring_payments', 'enabled'),
                getattr(settings, 'MERCHANT_LOGIN', ''),
                getattr(settings, 'MERCHANT_TXN_KEY', '')
                ]):
            call_command('make_recurring_payment_transactions')
