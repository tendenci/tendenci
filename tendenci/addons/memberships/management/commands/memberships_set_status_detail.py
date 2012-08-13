from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Resets membership to expired or inactive.
    """
    def handle(self, *args, **options):
        from datetime import datetime
        from tendenci.addons.memberships.models import Membership
        verbosity = int(options['verbosity'])

        # memberships will remain "expired" because of their dt
        expired = Membership.objects.filter(expire_dt__lt=datetime.now(), status_detail='expired'
            ).update(status_detail='active')

        # memberships will be set to inactive; setting them to 'expired' was a workaround
        inactive = Membership.objects.filter(expire_dt__gte=datetime.now(), status_detail='expired'
            ).update(status_detail='inactive')

        if verbosity:
            print 'Success!', '%s set to expired and %s set to inactive.' % (expired, inactive)
