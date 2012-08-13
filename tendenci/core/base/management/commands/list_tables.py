import os
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
                    
        def sort_table_list(table_list, rel_table, table):
            i = table_list.index(rel_table)
            try:
                j = table_list.index(table)
                if j<i:
                    del table_list[i]
                    table_list.insert(j, rel_table)
            except:
                table_list.append(table)
            
                
        for table in models_d.keys():
            if table not in tables_list:
                tables_list.append(table)
                
            for field in models_d[table]._meta.fields:
                if isinstance(field, ForeignKey) \
                    or isinstance(field, OneToOneField):
                    # get the related table
                    rel_table = field.rel.to._meta.db_table
                    if rel_table not in tables_list:
                        tables_list.append(rel_table)
                    sort_table_list(tables_list, rel_table, table)
                    
        tables_list.remove('mig_help_files_helpfile_t4_to_t5')
        
        # copy the list to your conf.yml file.           
        print '-', '\n- '.join(tables_list)

                                
                        