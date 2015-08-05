import re
import os
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction, DEFAULT_DB_ALIAS
from StringIO import StringIO
from django.conf import settings


class Command(BaseCommand):
    """
    Example: python manage.py set_theme thinksmart
    """
    
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('theme_name')

    def handle(self, theme_name, **options):
        """
        Set the website theme via theme name
        """
        from tendenci.apps.site_settings.models import Setting

        try:
            setting = Setting.objects.get(
                name='theme',
                scope='module',
                scope_category='theme_editor',
            )
            setting.set_value(theme_name)
            setting.save()
            call_command('hide_settings', 'theme')
            call_command('update_settings', 'themes.%s' % theme_name.lstrip())
            call_command('clear_cache')
        except Setting.DoesNotExist:
            if int(options['verbosity']) > 0:
                print "We could not update the theme because the setting or theme is not available."


