from __future__ import print_function
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Converts all user.is_staff to user.is_superuser if user.is_active
        """
        # command to run: python manage.py admin_converter

        # all admins (under the new criteria or old criteria). make sure they are on admin group
        users = User.objects.filter(is_superuser=False,is_staff=True,is_active=True)
        for user in users:
            user.is_superuser = True
            user.save()

            print('User "%s(%s)" -- added' % (user.get_full_name(), user.username))
        print()
        count = len(users)
        if count == 1:
            print('1 user added.')
        else:
            print('%d users added.' % count)
