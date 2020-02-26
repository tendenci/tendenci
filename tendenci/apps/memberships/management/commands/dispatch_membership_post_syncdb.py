
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Dispatch membership post_migrate signal.
    Our memberships post_migrate handler creates new
    notice types and updates existing ones in the DB.
    """
    def handle(self, *args, **kwargs):
        from django.db.models.signals import post_migrate
        from django.db import DEFAULT_DB_ALIAS
        from tendenci.apps.notifications import models as notifications

        tuples = post_migrate.send(
            sender=notifications,
            app_config=notifications,
            verbosity=0,
            interactive=True,
            using=DEFAULT_DB_ALIAS,
        )

        for t in tuples:
            print('post_migrate handler', t[0])
