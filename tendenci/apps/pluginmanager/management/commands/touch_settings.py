import os
from django.core.management.base import BaseCommand
from django.db.transaction import commit_on_success


class Command(BaseCommand):

    @commit_on_success
    def handle(self, *args, **kwargs):
        from django.conf import settings
        wsgi = os.path.join(settings.PROJECT_ROOT, 'conf', 'wsgi.py')
        settings_path = os.path.join(settings.PROJECT_ROOT, 'conf', 'settings.py')
        os.system('touch ' + wsgi)
        os.system('touch ' + settings_path)
