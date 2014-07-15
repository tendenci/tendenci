from optparse import make_option
from django.conf import settings
from django.core.management.base import CommandError, NoArgsCommand


class Command(NoArgsCommand):
    """
    Download themes from S3 to the local themes directory.

    Usage:
        manage.py download_themes_from_s3 --update-only --dry-run
        manage.py download_themes_from_s3 --update-only
        manage.py download_themes_from_s3
    """
    option_list = NoArgsCommand.option_list + (
        make_option('-n', '--dry-run',
            action='store_true', dest='dry_run', default=False,
            help="Do everything except modify the filesystem."),
        make_option('-u', '--update-only', action='store_true',
            dest='update_only', default=False,
            help="Update based on the last modified timestamp. "),
    )
    help = "Dowload themes from S3 to the local themes directory"


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
