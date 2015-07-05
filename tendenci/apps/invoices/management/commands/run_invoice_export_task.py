from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model


class Command(BaseCommand):
    args = '<export_pk, start_dt, end_dt>'
    help = "Runs an export task for invoices."

    def add_arguments(self, parser):
        parser.add_argument('export_id', type=int)
        parser.add_argument('start_dt')
        parser.add_argument('end_dt')
        
    def handle(self, *args, **options):
        from tendenci.apps.exports.models import Export
        from tendenci.apps.invoices.tasks import InvoiceExportTask
        export_id = options['export_id']
        start_dt = options['start_dt']
        end_dt = options['end_dt']
        if export_id:
            try:
                export = Export.objects.get(pk=export_id)
            except Export.DoesNotExist:
                raise CommandError('Export not specified')

            self.stdout.write('Started compiling export file...')

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
