from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model


class Command(BaseCommand):
    args = '<export_pk, start_dt, end_dt>'
    help = "Runs an export task for invoices."

    def handle(self, *args, **options):
        from tendenci.core.exports.models import Export
        from tendenci.apps.invoices.tasks import InvoiceExportTask
        if args:

            try:
                export = Export.objects.get(pk=int(args[0]))
            except Export.DoesNotExist:
                raise CommandError('Export not specified')

            self.stdout.write('Started compiling export file...')

            start_dt = args[1]
            end_dt = args[2]

            model = get_model(export.app_label, export.model_name)
            result = InvoiceExportTask()
            file_name = export.model_name + '.csv'
            response = result.run(model, start_dt, end_dt, file_name)

            export.status = "completed"
            export.result = response
            export.save()

            self.stdout.write('Successfully completed export file.')
        else:
            raise CommandError('Export args not specified')
