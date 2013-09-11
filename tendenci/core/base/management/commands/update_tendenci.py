import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Update tendenci via pip and restarts the server
    """
    def handle(self, *args, **kwargs):
        print "Updating tendenci"
        os.system('pip install tendenci --upgrade')

        print "Restarting Server"
        # This depends on the server used, please update accordingly
        os.system('service tendencisite restart')
        os.system('service nginx restart')
