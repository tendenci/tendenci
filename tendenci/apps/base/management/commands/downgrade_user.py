import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    """
    Downgrades a user to just a regular user

    This command does the following to the user account:
        * Removes them from all groups
        * Removes all user level permissions
        * Sets is_staff to 0
        * Sets is_superuser to 0
        * Sets is_active to 1
        * Removes them from all tendenci user_groups
    """
    option_list = BaseCommand.option_list + (
        make_option('--username',
            action='store',
            dest='username',
            default=None,
            help='Username of the user account being downgraded'),
        )

    def handle(self, *args, **options):
        from tendenci.apps.user_groups.models import GroupMembership

        verbosity = options['verbosity']
        username = options['username']

        if not username:
            raise CommandError('downgrade_user: --username parameter is required')

        # get the user
        try:
            u = User.objects.get(username=username)
        except ObjectDoesNotExist:
            print 'User with username (%s) could not be found' % username
            return

        # Remove the user from all groups
        u.groups.clear()

        # Remove all user-level permissions
        u.user_permissions.clear()

        # Reset permission bits
        u.is_staff = False
        u.is_superuser = False
        u.is_active = True
        u.save()

        # Remove the tendenci group permissions
        group_memberships = GroupMembership.objects.filter(member=u)
        for m in group_memberships:
            m.delete()

        if verbosity >= 2:
            print 'Done downgrading user (%s).' % u
