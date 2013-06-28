from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Clean old export files.

    Usage: python manage.py clean_old_exports
    """

    def handle(self, *args, **options):
        """
        Delete the export files that are older than 7 days
        """
        from tendenci.core.base.utils import directory_cleanup

        directory_cleanup('export', 7)
