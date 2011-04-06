from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    """
    This script is to sync the groups and subscribers with the campaign monitor 
    
    To run the command: python manage.py sync_campaign_monitor
    """
    
    def handle(self, *args, **options):
        verbosity = 1
        if 'verbosity' in options:
            verbosity = options['verbosity']

        pass