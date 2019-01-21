#run_nightly_commands.py

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    """
    Run a series of commands that should be run on a
    nightly (daily) basis.
    """
    def handle(self, *args, **options):
        commands = ('expire_jobs',
                    'expire_resumes',
                    'expire_stories',
                    'send_event_reminders',
                    "check_abandoned_payments",
                    'clean_corporate_memberships',
                    'send_membership_notices',
                    'clean_memberships',
                    'refresh_membership_groups',
                    'send_corp_membership_notices',
                    'clean_old_exports',
                    'clean_old_imports',
                    #'delete_soft_deleted_items',
                    'update_dashboard_stats',
                    'collect_metrics',
                    'captcha_clean',
                    'cleanup_expired_dbdumps',
                    'clearsessions',
                    'make_recurring_payment_transactions',
                    )
        for c in commands:
            try:
                call_command(c)
            except:
                pass
