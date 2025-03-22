from django.core.management.base import BaseCommand
from tendenci.apps.site_settings.utils import get_setting


class Command(BaseCommand):
    """
    If the Global site setting 'keep_event_log_for_days' is not zero,
    then delete all event_logs_eventlog records older than 
    'keep_event_log_for_days' days

    Usage: python manage.py prune_event_log_records
    """

    def handle(self, *args, **options):
        from tendenci.apps.event_logs.models import EventLog
        from datetime import datetime, timedelta

        days_to_keep_eventlog = get_setting('site', 'global', 'keep_event_log_for_days')

        if days_to_keep_eventlog > 0:
            cutoff_date = datetime.now() - timedelta(days = days_to_keep_eventlog)
            deleted_count = EventLog.objects.filter(create_dt__lte=cutoff_date).delete()[0]
            if deleted_count > 0:
                print("{} EventLog records were deleted as they were older than {}".format(deleted_count, cutoff_date.strftime("%d %b %Y %H:%M:%S")))
            else:
                print("{} No EventLog records older than {} so none deleted".format(deleted_count, cutoff_date.strftime("%d %b %Y %H:%M:%S")))
        else:
            print("'keep_event_log_for_days' setting is 0, EventLog record pruning skipped")
