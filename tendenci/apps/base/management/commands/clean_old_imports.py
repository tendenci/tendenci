from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Clean old import files.

    Usage: python manage.py clean_old_imports
    """

    def handle(self, *args, **options):
        """
        Remove the import files that are older than 7 days
        """
        from tendenci.apps.base.utils import directory_cleanup

        directory_cleanup('imports', 7)
