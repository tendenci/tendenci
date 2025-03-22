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
        import datetime

        days_to_keep_eventlog = get_setting('site', 'global', 'keep_event_log_for_days')

        if days_to_keep_eventlog > 0:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days = days_to_keep_eventlog)
            EventLog.objects.filter(create_dt__lte=cutoff_date).delete()
