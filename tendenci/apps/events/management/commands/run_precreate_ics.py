from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model


class Command(BaseCommand):
    args = '<ics_pk>'
    help = "Runs an export task for the specified model."

    def handle(self, *args, **options):
        try:
            from tendenci.apps.events.ics.models import ICS
            from tendenci.apps.events.tasks import EventsICSTask
            
            if args:
                try:
                    ics = ICS.objects.get(pk=int(args[0]))
                except Export.DoesNotExist:
                    raise CommandError('ICS not specified')
                 
                self.stdout.write('Started compiling ics file...')
    
                
                result = EventsICSTask()
                response = result.run(ics=ics)
    
                ics.status = "completed"
                ics.result = response
                ics.save()
    
                self.stdout.write('Successfully completed ics file.')
            else:
                raise CommandError('ICS args not specified')
        except ImportError:
            print "Cannot precreate ics because events app is not installed."
