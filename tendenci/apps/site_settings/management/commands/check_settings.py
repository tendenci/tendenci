
import os
import simplejson as json

from django.core.management.base import BaseCommand, CommandError

from tendenci.apps.site_settings.models import Setting


class Command(BaseCommand):
    """
    Use this command to check settings in the database

    Reads from the json file located in the same
    directory as this file and loops though it.

    Optional Command Arguments:
        `json`: path to the json file

    Json required fields (for lookups):
        `scope`
        `scope_category`
        `name`

    Json format:
        [
          {
            "name": "",
            "scope": "",
            "scope_category": "",
          }
        ]
    """
    help = 'Check a setting in the site_settings_setting table'

    def check_settings(self, settings):
        """
        Loop through the settings and check them
        """
        required_keys = [
            'scope',
            'scope_category',
            'name'
        ]
        for setting in settings:
            # check the required fields
            req_list = [k for k in setting if k in required_keys]
            if len(req_list) != len(required_keys):
                print('Setting does not have the required fields ... skipping.')
                continue

            try:
                Setting.objects.get(**{
                    'name': setting['name'],
                    'scope': setting['scope'],
                    'scope_category': setting['scope_category']
                })
            except Setting.DoesNotExist:
                print("Setting: %s %s %s, is missing." % (setting['name'], setting['scope'], setting['scope_category']))

    def handle(self, *args, **options):
        json_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'check_settings.json')
        )

        if 'json' in options:
            json_file = options['json']

        if os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                try:
                    settings = json.loads(f.read())
                except ValueError as e:
                    raise CommandError(e)
                self.check_settings(settings)
        else:
            raise CommandError('%s: Could not find json file %s' % (
                __file__,
                json_file,
            ))
