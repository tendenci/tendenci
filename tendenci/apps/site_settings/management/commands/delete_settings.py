from django.core.management.base import BaseCommand
from tendenci.apps.site_settings.models import Setting


class Command(BaseCommand):
    """
    Use this command to delete a setting form the database

    Delets the setting(s) specified.  More than one setting
    can be specified (space delimited).
    """

    help = """
    Delete a setting from the site_settings_setting table.
    Examples:
    To delete a specific setting: delete_settings module/articles/articlerecipients
    To delete all settings for a specific module: delete_settings module/articles
    """

    def handle(self, *settings, **options):
        verbosity = options['verbosity']

        # example if no settings are passed.
        if not settings and verbosity > 0:
            print self.help

        for setting in settings:
            if setting.count('/') == 2:
                scope, scope_category, name = setting.split('/')

                try:
                    setting = Setting.objects.get(scope=scope, scope_category=scope_category, name=name)
                    setting.delete()
                    message = 'Deleted %s:%s:%s' % (setting.scope, setting.scope_category, setting.name)
                except Setting.DoesNotExist:
                    message = "Does Not Exist %s:%s:%s" % (scope, scope_category, name)
                except Setting.MultipleObjectsReturned:
                    message = "Multiple Results!? %s:%s:%s" & (scope, scope_category, name)

                if verbosity > 0:
                    print message

            elif setting.count('/') == 1:
                scope, scope_category = setting.split('/')

                setting = Setting.objects.filter(scope=scope, scope_category=scope_category)
                if setting:
                    setting.delete()
                    message = 'Deleted settings for %s:%s' % (scope, scope_category)
                else:
                    message = "Does Not Exist %s:%s" % (scope, scope_category)

                if verbosity > 0:
                    print message
