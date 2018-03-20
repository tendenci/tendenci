from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Download themes from S3 to the local themes directory.

    Usage:
        python manage.py download_themes_from_s3 --update-only --dry-run
        python manage.py download_themes_from_s3 --update-only
        python manage.py download_themes_from_s3
    """
    help = "Download themes from S3 to the local themes directory"

    def add_arguments(self, parser):
        parser.add_argument('-n', '--dry-run',
            action='store_true', dest='dry_run', default=False,
            help="Do everything except modify the filesystem.")
        parser.add_argument('-u', '--update-only', action='store_true',
            dest='update_only', default=False,
            help="Update based on the last modified timestamp. ")

    def set_options(self, **options):
        """
        Set instance variables based on an options dict
        """
        self.update_only = options['update_only']
        self.dry_run = options['dry_run']

    def handle_noargs(self, **options):
        from tendenci.libs.boto_s3.utils import download_files_from_s3

        self.set_options(**options)

        download_files_from_s3(prefix='themes',
                               to_dir=settings.ORIGINAL_THEMES_DIR,
                               dry_run=self.dry_run,
                               update_only=self.update_only)
