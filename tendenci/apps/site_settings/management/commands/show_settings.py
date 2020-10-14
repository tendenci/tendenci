import simplejson as json
from io import StringIO
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Example: python manage.py show_settings
    """
    def handle(self, *args, **kwargs):
        """
        Prints a summary of current site settings in format "scope/category/name = value"    
        """
        string_io = StringIO()
        call_command('dumpdata', 'site_settings', stdout=string_io)
        string_io.seek(0)
        s = json.loads(string_io.read())

        for setting in s:
            scope = setting["fields"]["scope"]
            category = setting["fields"]["scope_category"]
            name = setting["fields"]["name"]
            #label = setting["fields"]["label"]  # Not used currently (could be optionally displayed)
            value = setting["fields"]["value"]
            print(f'{scope}/{category}/{name} = {value}')
