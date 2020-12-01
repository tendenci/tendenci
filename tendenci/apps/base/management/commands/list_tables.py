
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps as django_apps


class Command(BaseCommand):
    """
    Generate a list of tables.

    Usage: manage.py list_tables
    """

    def handle(self, *args, **options):
        apps = []

        for app in settings.INSTALLED_APPS:
            try:
                app_label = app.split('.')[-1]
                apps.append(app_label)
            except:
                # No models, no problem.
                pass

        for app_label in apps:
            # skip the legacy
            if app_label in ['legacy']:
                continue
            # skip the social_auth if not set
            if not getattr(settings, 'SOCIAL_AUTH_USER_MODEL', None):
                if app_label in  ['social_auth']:
                    continue

            for model in django_apps.get_app_config(app_label).get_models(include_auto_created=True):
                print(model._meta.db_table)
