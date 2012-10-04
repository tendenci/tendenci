from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

from tendenci.core.imports import Import
from tendenci.addons.events.utils import event_import_process

class Command(BaseCommand):
    args = '<import_pk>'
    help = "Runs an import task for the specified model."

    def handle(self, *args, **options):
        if args:

            try:
                export = Import.objects.get(pk=int(args[0]))
            except Import.DoesNotExist:
                raise CommandError('Export not specified')

            self.stdout.write('Started importing import file...')

            event_import_process(import_i, preview=False)

            self.stdout.write('Successfully completed import process.')
        else:
            raise CommandError('Import args not specified')
