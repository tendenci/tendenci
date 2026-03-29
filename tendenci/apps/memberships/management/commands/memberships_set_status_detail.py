from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    """
    Resets membership to expired or active.
    """
    def handle(self, *args, **options):
        from datetime import datetime
        from tendenci.apps.memberships.models import MembershipDefault
        verbosity = int(options['verbosity'])

        # memberships will remain "expired" because of their dt
        expired = MembershipDefault.objects.filter(expire_dt__lt=timezone.now(), status_detail='active'
            ).update(status_detail='expired')

        # memberships will be set to active because of the expire_dt
        active = MembershipDefault.objects.filter(expire_dt__gt=timezone.now(), status_detail='expired'
        ).update(status_detail='active')

        if verbosity:
            print('Success!', '{} set to expired and {} set to active.'.format(expired, active))
