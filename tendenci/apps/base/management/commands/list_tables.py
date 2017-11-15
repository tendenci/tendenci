from __future__ import print_function
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import get_models, get_app
from django.db.models import ForeignKey, OneToOneField


class Command(BaseCommand):
    """
    Generate a list of tables and sort them based on the relations
    for db migration from mysql to postgresql.

    Usage: manage.py list_tables
    """

    def handle(self, *args, **options):
        apps = []
        models_d = {}
        tables_list = []
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
            try:
                app = get_app(app_label)
            except:
                app = None
            if app:
                for model in get_models(app, include_auto_created=True):
                    models_d[model._meta.db_table] = model
                    tables_list.append(model._meta.db_table)

        tables_list.remove('mig_help_files_helpfile_t4_to_t5')
        # django 1.4 doesn't have auth_message table
        if 'auth_message' in tables_list:
            tables_list.remove('auth_message')

        related_tables = {}
        # get a list of related tables for each table
        for table in tables_list:
            related_tables[table] = [field.rel.to._meta.db_table \
                        for field in models_d[table]._meta.fields \
                        if isinstance(field, (ForeignKey, OneToOneField))
                        and field.rel.to._meta.db_table != table
                        ]

        sorted_list = []
        for table in tables_list:
            if not related_tables[table]:
                sorted_list.append(table)

        n = 100
        # avoid getting into the infinite loop - just in case
        #while related_tables:
        while n > 1:
            # remove tables from related_tables if already in the sorted_list
            for key in related_tables.keys():
                for rel_table in related_tables[key]:
                    if rel_table in sorted_list:
                        related_tables[key].remove(rel_table)
                if not related_tables[key]:
                    del related_tables[key]

            # add to the sorted_list if there is no
            # related_tables  for this table
            for table in tables_list:
                # if the related_tables is gone
                if table not in sorted_list and (
                       table not in related_tables.keys()):
                    sorted_list.append(table)

            # continue until all the related tables are gone
            if not related_tables:
                break

            n = n - 1

        if related_tables:
            print("ERROR: Sorting not completed.")

        # copy the list to your conf.yml file
        print('-', '\n- '.join(sorted_list))
