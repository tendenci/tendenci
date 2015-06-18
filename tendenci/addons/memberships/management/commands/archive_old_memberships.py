from django.core.management.base import BaseCommand
from django.db.models import Count


class Command(BaseCommand):
    """
    Set the status_detail to 'archive' for old memberships
    if they are not equal to 'archive'. In the meantime,
    set renewal bit to True for the current one if it
    has archive records.

    Usage: python manage.py archive_old_memberships --verbosity 2
    """

    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']

        from tendenci.addons.memberships.models import MembershipDefault

        duplicate_user_ids = MembershipDefault.objects.values_list(
                                        'user__id', flat=True
                                        ).annotate(
                                         num_users=Count('user__id')
                                        ).filter(num_users__gt=1
                                        ).exclude(
                                        status_detail='archive')
        for user_id in duplicate_user_ids:
            memberships = MembershipDefault.objects.filter(
                                user__id=user_id
                                ).order_by('-expire_dt',
                                           '-create_dt')
            if len(memberships) > 1:
                skip_renewal_bit_update = False
                first_membership = memberships[0]
                if first_membership.status_detail != 'active':
                    continue

                for membership in memberships:
                    if membership.id == first_membership.id:
                        # skip the first one
                        continue
                    if membership.expire_dt == first_membership.expire_dt \
                        and membership.status_detail == \
                        first_membership.status_detail \
                        and membership.membership_type_id \
                        != first_membership.membership_type_id:
                        # skip if same expire_dt and status_detail but
                        # different membership type
                        skip_renewal_bit_update = True
                        continue

                    if membership.status_detail != 'archive':
                        membership.status_detail = 'archive'
                        membership.save()
                        if verbosity > 1:
                            print 'Archived for membership ID=%d' % membership.id

                if not first_membership.renewal:
                    if not skip_renewal_bit_update:
                        first_membership.renewal = True
                        first_membership.save()
                        if verbosity > 1:
                            print 'Set renewal=True for membership ID=%d' % first_membership.id
        print 'Done'
