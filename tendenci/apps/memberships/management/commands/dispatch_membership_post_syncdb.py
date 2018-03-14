from __future__ import print_function
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Dispatch membership post_migrate signal.
    Our memberships post_migrate handler creates new
    notice types and updates existing ones in the DB.
    """
    def handle(self, *args, **kwargs):
        from django.db.models.signals import post_migrate
        from tendenci.apps.notifications import models as notifications

        tuples = post_migrate.send(
            sender=notifications,
            app=None,
            created_models=False,
            verbosity=0,
        )

        for t in tuples:
            print('post_migrate handler', t[0])
