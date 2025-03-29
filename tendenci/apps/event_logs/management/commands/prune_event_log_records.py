from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """
    If the Django setting 'KEEP_EVENT_LOG_FOR_DAYS' is not zero,
    then delete all event_logs_eventlog records older than 
    'KEEP_EVENT_LOG_FOR_DAYS' days

    Usage: python manage.py prune_event_log_records
    """

    def handle(self, *args, **options):
        from tendenci.apps.event_logs.models import EventLog
        from datetime import datetime, timedelta

        if settings.KEEP_EVENT_LOG_FOR_DAYS > 0:
            cutoff_date = datetime.now() - timedelta(days = settings.KEEP_EVENT_LOG_FOR_DAYS)
            deleted_count = EventLog.objects.filter(create_dt__lte=cutoff_date).delete()[0]
            if deleted_count > 0:
                print("{} EventLog records were deleted as they were older than {}".format(deleted_count, cutoff_date.strftime("%d %b %Y %H:%M:%S")))
            else:
                print("{} No EventLog records older than {} so none deleted".format(deleted_count, cutoff_date.strftime("%d %b %Y %H:%M:%S")))
        else:
            print("'KEEP_EVENT_LOG_FOR_DAYS' setting is 0, EventLog record pruning skipped")
