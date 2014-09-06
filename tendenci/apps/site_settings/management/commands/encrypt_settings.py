import os
import simplejson as json

from django.conf import settings as django_settings
from django.core.management.base import BaseCommand, CommandError

from tendenci.apps.site_settings.models import Setting


class Command(BaseCommand):
    """Encrypts all Setting values if they are not already encrypted
    Usage:
        manage.py encrypt_settings
    """
    help = 'Encrypt all settings if they are not already encrypted'

    def handle(self, *args, **options):
        """Loop through the settings and use set_value for setting the values.
        Use set_value only when the setting is not yet marked secure.
        """
        settings = Setting.objects.all()
        for setting in settings:
            if not setting.is_secure:
                print "Encrypting %s %s %s" % (setting.scope, setting.scope_category, setting.name)
                setting.set_value(setting.value)
                setting.save()
