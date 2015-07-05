from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

class Command(BaseCommand):
    args = '<import_pk>'
    help = "Runs an import task for the specified model."

    def add_arguments(self, parser):
        parser.add_argument('import_id', type=int)

    def handle(self, *args, **options):
        from tendenci.apps.imports.models import Import
        from tendenci.apps.user_groups.importer.utils import user_groups_import_process
        import_id = options['import_id']
        if import_id:

            try:
                import_i = Import.objects.get(pk=import_id)
            except Import.DoesNotExist:
                raise CommandError('Export not specified')

            if import_i.status == "pending":
                self.stdout.write('Started importing import file...')

                user_groups_import_process(import_i, preview=False)

                self.stdout.write('Successfully completed import process.')
            elif import_i.status == "completed":
                self.stdout.write("Import has already been completed.")
            elif import_i.status == "processing":
                self.stdout.write("Import is still being processed.")
            else:
                self.stdout.write("Import failed.")
        else:
            raise CommandError('Import args not specified')
