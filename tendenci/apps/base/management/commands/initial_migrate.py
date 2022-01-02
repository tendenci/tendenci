from django.core.management.base import no_translations
from django.core.management.commands.migrate import Command as MigrateCommand

class Command(MigrateCommand):
    # The system checks import urls.py, which imports lots of other modules
    # which attempt to access the database.  This will prevent the database from
    # being initialized.  To work around that, disable the system checks on the
    # initial migration.

    @no_translations
    def handle(self, *args, **options):
        options['skip_checks'] = True
        super(Command, self).handle(*args, **options)
