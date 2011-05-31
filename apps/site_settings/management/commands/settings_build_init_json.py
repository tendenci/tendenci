import simplejson as json
from StringIO import StringIO
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Example: python manage.py settings_build_init_json.py
    """
    def handle(self, *args, **kwargs):
        """
        Build the initial settings json file via DB records
        """
        string_io = StringIO()
        call_command('dumpdata', 'site_settings', stdout=string_io)
        string_io.seek(0)
        s = json.loads(string_io.read())

        field_sets = [i['fields'] for i in s]

        json_dumps = json.dumps(field_sets, indent=4)

        f = open('settings.json', 'w')
        f.write(json_dumps)
        f.close()
