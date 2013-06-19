from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Add any missing permissions
    """
    def handle(self, *args, **options):
        from django.contrib.auth.management import create_permissions
        from django.db.models import get_apps, get_models

        verbosity = int(options['verbosity'])

        for app in get_apps():
            create_permissions(app, None, verbosity)
