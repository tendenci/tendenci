import os, sys
from django.core.management.base import BaseCommand
from django.db.transaction import commit_on_success

class Command(BaseCommand):

    @commit_on_success
    def handle(self, *args, **kwargs):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../../../settings.py')
        wsgi = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../../../deploy/deploy.wsgi')
        os.system('touch '+path)
        os.system('touch '+wsgi)