from django.core.management.base import BaseCommand
from datetime import datetime, timedelta

class Command(BaseCommand):
    """
    Clean old export files.

    Usage: python manage.py clean_old_exports
    """

    def handle(self, *args, **options):
        """
        Delete the export files that are older than 7 days
        """
        from tendenci.apps.base.utils import directory_cleanup
        from tendenci.apps.exports.models import Export

        directory_cleanup('export', 7)
        
        # delete old exports from db
        for export in Export.objects.filter(date_created__lt=(datetime.now() - timedelta(days=7))):
            export.delete()
