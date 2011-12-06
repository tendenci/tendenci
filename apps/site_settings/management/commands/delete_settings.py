from django.core.management.base import BaseCommand
from site_settings.models import Setting


class Command(BaseCommand):
    """
    Use this command to delete a setting form the database

    Delets the setting(s) specified.  More than one setting
    can be specified (space delimited).
    """
    help = 'Delete a setting from the site_settings_setting table'

    def handle(self, *settings, **options):
        Setting.objects.filter(name__in = settings).delete()