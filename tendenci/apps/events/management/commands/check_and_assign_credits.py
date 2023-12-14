from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Check and assign credits to registrants for a nested event.
    
    Usage:
    
        ./manage.py check_and_assign_credits --event_id=<event-id> --verbosity=2
    """
    def add_arguments(self, parser):
        parser.add_argument('--event_id',
            dest='event_id',
            default=None,
            help='The id of the event to be checked')

    def handle(self, *args, **options):
        from tendenci.apps.events.models import Event, Registrant, RegistrantChildEvent

        verbosity = options['verbosity']
        event_id = options['event_id']
        if not Event.objects.filter(id=event_id).exists():
            print('Event with event id ', event_id, "doesn't exist. Exiting")
            return

        event = Event.objects.get(id=event_id)
        if event.has_child_events:
            for child_event in event.all_child_events:
                if verbosity >= 2:
                    print('Processing child event:', child_event)
                for c_registrant in RegistrantChildEvent.objects.filter(
                                        child_event=child_event,
                                        checked_in=True):
                    if verbosity >= 2:
                        print(c_registrant.registrant)
                    child_event.assign_credits(c_registrant.registrant)
        else:
            for registrant in Registrant.objects.filter(
                        registration__event=event,
                        checked_in=True,
                        checked_out=True,
                        cancel_dt__isnull=True):
                reg8n = registrant.registration
                if reg8n.status() == 'registered':
                    print(registrant)
                    event.assign_credits(registrant)
        print('Done')
