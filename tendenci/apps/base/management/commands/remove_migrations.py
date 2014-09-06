from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Removes migrations for an app. Requires an app name to be passed"

    def handle(self, *args, **options):
        """Removes migrations for an app."""
        from south.models import MigrationHistory
        app_name = args[0]
        if app_name:
            migrations = MigrationHistory.objects.filter(app_name=app_name)
            if migrations:
                migrations.delete()
                print "Migrations for %s were removed" % app_name
            else:
                print "No migrations for %s" % app_name
