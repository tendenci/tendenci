from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Push unpushed items (users) to Authentik.
    
    Usage: python manage.py push_items_to_authentik --verbosity=2
    """

    def handle(self, **options):
        from ...models import UnPushedItem
        from ...utils import AuthentikAPI

        verbosity = int(options.get('verbosity', 0))
        items = UnPushedItem.objects.all().order_by('create_dt')
        if items:
            aut_api = AuthentikAPI()
            for item in items:
                if item.deleted:
                    res = aut_api.remove_user(item.user_id)
                    if verbosity >= 2:
                        print(res)
                else: 
                    user = User.objects.filter(id=item.user_id).first()
                    if user:
                        res = aut_api.push_user_to_authentik(user)
                        if verbosity >= 2:
                            print(res)

                item.delete()
                
        print('Done.')      
                