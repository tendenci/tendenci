from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Converts passwords with no hashing algorithm to use the default
        algorithm. These passwords are detected by measuring their length.
        """
        # command to run: python manage.py password_converter

        users = User.objects.exclude(password__regex = r'.{22}.*')
        for user in users:
            user.set_password(user.password)
            user.save()

        print "%s User passwords converted" % len(users)