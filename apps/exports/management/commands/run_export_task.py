from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

from exports.tasks import TendenciExportTask
from exports.models import Export

class Command(BaseCommand):
    args = '<export_pk, field, field, field...>'
    help = "Runs an export task for the specified model."
    
    def handle(self, *args, **options):
        if args:
            
            try:
                export = Export.objects.get(pk=int(args[0]))
            except Export.DoesNotExist:
                raise CommandError('Export not specified')
                
            model = get_model(export.app_label, export.model_name)
            result = TendenciExportTask()
            file_name = export.model_name+'.csv'
            response = result.run(model, args[1:], file_name)
            export.status = "completed"
            export.result = response
            export.save()
            self.stdout.write('Successfully completed export.')
        else:
            raise CommandError('Export args not specified')
