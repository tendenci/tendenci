from django.core.management.commands.migrate import Command as MigrateCommand

class Command(MigrateCommand):
    # The system checks import urls.py, which imports lots of other modules
    # which attempt to access the database.  This will prevent the database from
    # being initialized.  To work around that, disable the system checks on the
    # initial migration.
    requires_system_checks = False
