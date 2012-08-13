from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Dispatch membership post_syncdb signal.
    Our memberships post_syncdb handler creates new
    notice types and updates existing ones in the DB.
    """
    def handle(self, *args, **kwargs):
        from django.db.models.signals import post_syncdb
        from tendenci.apps.notifications import models as notifications

        tuples = post_syncdb.send(
            sender=notifications,
            app=None,
            created_models=False,
            verbosity=0,
        )

        for t in tuples:
            print 'post_syncdb handler', t[0]