import re
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction, DEFAULT_DB_ALIAS
from django.conf import settings

class Command(BaseCommand):
    """
        Use this command to update settings on a site that has already been created
        and needs some settings to be updated.
        eg. description, default_value
        
        WARNING: DO NOT USE TO UPDATE VALUE!!
    """
    help = 'Makes updates to settings on sites that already exist'

    def handle(self, *args, **options):
        # file and path information
        root_path = os.path.abspath(os.path.dirname(__file__))
        sql_file = os.path.join(root_path,'update_settings.sql')
        
        # database information
        using = options.get('database', DEFAULT_DB_ALIAS)
        connection = connections[using]
        
        # sql statement regex
        statements = re.compile(r";[ \t]*$", re.M)
        sql_list = []
        
        # update the sql
        if os.path.exists(sql_file):
            fp = open(sql_file, 'U')
            for statement in statements.split(fp.read().decode(settings.FILE_CHARSET)):
                # Remove any comments from the file
                statement = re.sub(ur"--.*([\n\Z]|$)", "", statement)
                if statement.strip():
                    sql_list.append(statement + u";")
            fp.close()
            
            if sql_list:
                try:
                    cursor = connection.cursor()
                    for sql in sql_list:
                        cursor.execute(sql)
                except Exception, e:
                    transaction.rollback_unless_managed()
                    raise CommandError("""Error running SQL. Possible reasons:
      * The database isn't running or isn't configured correctly.
      * At least one of the database tables doesn't exist.
      * The SQL was invalid.
    The full error: %s""" % (e))
                transaction.commit_unless_managed()
                print 'Successfully executed %d statements.' % len(sql_list)
            else:
                raise CommandError('SQL file %s is empty' % sql_file)
        else:
            raise CommandError('SQL file is missing. "update_settings.sql" must exist in management command path %s.' % root_path)