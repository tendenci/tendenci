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
            
            self.stdout.write('Started compiling export file...')
            
            # special case models
            if export.app_label == 'events' and export.model_name == 'event':
                from events.tasks import EventsExportTask
                result = EventsExportTask()
                response = result.run()
            elif export.app_label == 'forms_builder.forms' and export.model_name == 'form':
                from forms_builder.forms.tasks import FormsExportTask
                result = FormsExportTask()
                response = result.run()
            elif export.app_label == 'navs' and export.model_name == 'nav':
                from navs.tasks import NavsExportTask
                result = NavsExportTask()
                response = result.run()
            else:
                model = get_model(export.app_label, export.model_name)
                result = TendenciExportTask()
                file_name = export.model_name+'.csv'
                response = result.run(model, args[1:], file_name)
                
            export.status = "completed"
            export.result = response
            export.save()
            
            self.stdout.write('Successfully completed export file.')
        else:
            raise CommandError('Export args not specified')
