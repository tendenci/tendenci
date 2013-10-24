import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from tendenci.core.base.models import UpdateTracker

class Command(BaseCommand):
    """
    Update tendenci via pip and restarts the server
    """
    def handle(self, *args, **kwargs):
        UpdateTracker.start()
        print "Updating tendenci package"
        os.system('pip install tendenci --upgrade')

        print "Updating tendenci site"
        os.system('python deploy.py')

        print "Restarting Server"
        os.system('sudo reload %s' % os.path.basename(settings.PROJECT_ROOT))
        
        UpdateTracker.end()
        call_command('clear_cache')
