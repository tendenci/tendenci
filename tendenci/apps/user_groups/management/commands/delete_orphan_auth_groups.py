from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group as AuthGroup
from johnny.cache import invalidate


class Command(BaseCommand):
    """"
    Delete the orphan auth groups (An orphan auth group refers to
    the one without a user group associated with it.)

    Usage: ./manage.py delete_orphan_auth_groups
    """

    def handle(self, *args, **options):
        from tendenci.apps.user_groups.models import Group

        invalidate('user_groups_group')
        invalidate('auth_group')
        tied_auth_group_ids = Group.objects.all(
                                    ).values_list('group',
                                                  flat=True)
        orphan_auth_groups = AuthGroup.objects.all().exclude(
                                id__in=tied_auth_group_ids)
        for auth_group in orphan_auth_groups:
            auth_group.delete()
