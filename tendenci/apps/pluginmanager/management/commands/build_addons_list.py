from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, **options):
        """
        Build the list of addons to be used when Django loads
        """
        pass
