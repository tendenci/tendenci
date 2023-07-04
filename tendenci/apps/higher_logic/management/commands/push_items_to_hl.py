from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Push unpushed items (users and events) to Higher Logic.
    
    Usage: python manage.py push_items_to_hl --verbosity=2
    """

    def handle(self, **options):
        from tendenci.apps.higher_logic.models import UnPushedItem
        from tendenci.apps.higher_logic.utils import HigherLogicAPI
        from tendenci.apps.events.models import Event

        verbosity = int(options.get('verbosity', 0))
        items = UnPushedItem.objects.all().order_by('create_dt')
        if items:
            hc = HigherLogicAPI()
            for item in items:
                if item.user_id and item.identifier:
                    [user] = User.objects.filter(id=item.user_id)[:1] or [None]
                    if user:
                        hc.push_user_info([user])
                        if verbosity >= 2:
                            print('Pushed user ', user)
                    else:
                        hc.remove_user(item.identifier)
                        if verbosity >= 2:
                            print(f'Removed user with account_id {item.identifier} from HL')
                        
                if item.event_id and item.identifier:
                    [event] = Event.objects.filter(id=item.event_id)[:1] or [None]
                    if event:
                        if not item.deleted:
                            hc.push_events([event])
                            if verbosity >= 2:
                                print('Pushed event ', event)
                        else:
                            hc.remove_event(item.identifier)
                            if verbosity >= 2:
                                print(f'Removed event {item.identifier} from HL')
                    else:
                        # event doesn't exist, remove it from HL
                        hc.remove_event(item.identifier)
                        if verbosity >= 2:
                            print(f'Removed event {item.identifier} from HL')

                item.delete()
                
        print('Done.')      
                