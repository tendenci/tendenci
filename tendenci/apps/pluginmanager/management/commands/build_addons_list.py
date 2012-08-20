import os

from django.core.management.base import BaseCommand
from django.utils import simplejson


class Command(BaseCommand):

    def handle(self, **options):
        """
        Build the list of addons to be used when Django loads
        """
        from tendenci.apps.pluginmanager.models import db2json
        from django.conf import settings

        db2json()
        json_data_path = os.path.join(settings.PROJECT_ROOT, 'addons_list.json')
        f = open(json_data_path, 'r')
        data = ''.join(f.read())
        print "addons_list.json: ", simplejson.loads(data)
        f.close()
