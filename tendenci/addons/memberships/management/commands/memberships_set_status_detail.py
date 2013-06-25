from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Resets membership to expired or inactive.
    """
    def handle(self, *args, **options):
        from datetime import datetime
        from tendenci.addons.memberships.models import MembershipDefault
        verbosity = int(options['verbosity'])

        # memberships will remain "expired" because of their dt
        expired = MembershipDefault.objects.filter(expire_dt__lt=datetime.now(), status_detail='expired'
            ).update(status_detail='active')

        # memberships will be set to inactive; setting them to 'expired' was a workaround
        inactive = MembershipDefault.objects.filter(expire_dt__gte=datetime.now(), status_detail='expired'
            ).update(status_detail='inactive')
        
        # memberships will be set to active because of the expire_dt
        active = MembershipDefault.objects.filter(expire_dt__gt=datetime.now(), status_detail='expired'
        ).update(status_detail='active')


        if verbosity:
            print 'Success!', '%s set to expired and %s set to inactive and %s set to active.' % (expired, inactive, active)
