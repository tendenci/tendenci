from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    Cleanup Expired DB Dumps

    Usage:
        python manage.py cleanup_expired_dbdumps

    """
    def handle(self, *args, **options):
        import datetime
        from tendenci.apps.explorer_extensions.models import DatabaseDumpFile
        print "Start of db dump cleanup"
        for df in DatabaseDumpFile.objects.all():
            if df.end_dt and df.end_dt < datetime.datetime.now():
                print "Deleting DB dump file (pk=%d)" % df.id
                df.delete()
        print "End of db dump cleanup"
