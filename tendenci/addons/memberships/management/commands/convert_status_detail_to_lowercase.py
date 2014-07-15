from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Convert status_detail to lowercase. With the update function,
    we only update the status_detail field
    .
    """
    def handle(self, *args, **options):
        from tendenci.addons.memberships.models import MembershipDefault

        # active
        MembershipDefault.objects.filter(status_detail__iexact='Active'
                                         ).exclude(status_detail='active'
                                                   ).update(status_detail='active')
        # expired
        MembershipDefault.objects.filter(status_detail__iexact='Expired'
                                         ).exclude(status_detail='expired'
                                                   ).update(status_detail='expired')
        # pending
        MembershipDefault.objects.filter(status_detail__iexact='Pending'
                                         ).exclude(status_detail='pending'
                                                   ).update(status_detail='pending')
        # archive
        MembershipDefault.objects.filter(status_detail__iexact='Archive'
                                         ).exclude(status_detail='archive'
                                                   ).update(status_detail='archive')
