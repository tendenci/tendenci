from django.core.management.base import BaseCommand, CommandError
from django.apps import apps


class Command(BaseCommand):
    args = '<export_pk, field, field, field...>'
    help = "Runs an export task for the specified model."

    def add_arguments(self, parser):
        parser.add_argument('export_id', type=int)
        parser.add_argument('fields', nargs='*')
        parser.add_argument(
            '--start_dt',
            action='store',
            dest='start_dt',
            default='',
            help='Export start date is greater than or equal to the value specified')
        parser.add_argument(
            '--end_dt',
            action='store',
            dest='end_dt',
            default='',
            help='Export end date is less than the value specified')
        parser.add_argument(
            '--include_files',
            action='store',
            dest='include_files',
            default=False,
            help='Specify whether or not to include the uploaded files (default to False)')

    def handle(self, *args, **options):
        from tendenci.apps.exports.models import Export
        from tendenci.apps.exports.tasks import TendenciExportTask
        export_id = options['export_id']
        fields = options['fields']
        start_dt = options['start_dt']
        end_dt = options['end_dt']
        include_files = options['include_files']

        if start_dt and end_dt:
            kwargs = {'start_dt': start_dt,
                      'end_dt': end_dt}
        else:
            kwargs = {}
        if include_files:
            kwargs.update({'include_files': include_files})
        if export_id:
            try:
                export = Export.objects.get(pk=export_id)
            except Export.DoesNotExist:
                raise CommandError('Export not specified')

            self.stdout.write('Started compiling export file...')

            # special case models
            if export.app_label == 'events' and export.model_name == 'event':
                from tendenci.apps.events.tasks import EventsExportTask
                result = EventsExportTask()
                response = result.run()
            elif export.app_label == 'forms_builder.forms' and export.model_name == 'form':
                from tendenci.apps.forms_builder.forms.tasks import FormsExportTask
                result = FormsExportTask()
                response = result.run()
            elif export.app_label == 'navs' and export.model_name == 'nav':
                from tendenci.apps.navs.tasks import NavsExportTask
                result = NavsExportTask()
                response = result.run()
            elif export.app_label == 'pages' and export.model_name == 'page':
                from tendenci.apps.pages.tasks import PagesExportTask
                result = PagesExportTask()
                response = result.run()
            elif export.app_label == 'profiles' and export.model_name == 'profile':
                from tendenci.apps.profiles.tasks import ExportProfilesTask
                result = ExportProfilesTask()
                response = result.run()
            else:
                model = apps.get_model(export.app_label, export.model_name)
                result = TendenciExportTask()
                file_name = export.app_label + '.csv'
                response = result.run(model, fields, file_name, **kwargs)

            export.status = "completed"
            export.result = response
            export.save()

            self.stdout.write('Successfully completed export file.')
        else:
            raise CommandError('Export args not specified')
