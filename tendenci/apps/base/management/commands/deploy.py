from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    """
    Deploy a new version of Tendenci.
    """
    def handle(self, *args, **options):
        call_command('collectstatic', '--link', '--noinput')
        call_command('update_settings')
        call_command('clear_theme_cache')
        call_command('populate_default_entity')
        call_command('populate_entity_and_auth_group_columns')
        call_command('loaddata', 'initial_data.json')
