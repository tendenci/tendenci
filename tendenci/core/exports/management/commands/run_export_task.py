from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model


class Command(BaseCommand):
    args = '<export_pk, field, field, field...>'
    help = "Runs an export task for the specified model."

    def handle(self, *args, **options):
        from tendenci.core.exports.models import Export
        from tendenci.core.exports.tasks import TendenciExportTask
        if args:

            try:
                export = Export.objects.get(pk=int(args[0]))
            except Export.DoesNotExist:
                raise CommandError('Export not specified')

            self.stdout.write('Started compiling export file...')

            # special case models
            if export.app_label == 'events' and export.model_name == 'event':
                from tendenci.addons.events.tasks import EventsExportTask
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
#             elif export.app_label == 'memberships' and export.model_name == 'membership':
#                 from tendenci.addons.memberships.tasks import MembershipsExportTask
#                 kwargs = {'app': export.memb_app}
#                 result = MembershipsExportTask()
#                 response = result.run(**kwargs)
            elif export.app_label == 'profiles' and export.model_name == 'profile':
                from tendenci.apps.profiles.tasks import ExportProfilesTask
                result = ExportProfilesTask()
                response = result.run()
            else:
                model = get_model(export.app_label, export.model_name)
                result = TendenciExportTask()
                file_name = export.model_name + '.csv'
                response = result.run(model, args[1:], file_name)

            export.status = "completed"
            export.result = response
            export.save()

            self.stdout.write('Successfully completed export file.')
        else:
            raise CommandError('Export args not specified')
