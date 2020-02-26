
import re
import os
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction, DEFAULT_DB_ALIAS
from io import BytesIO
from django.conf import settings

# Remove Django color output handler
os.environ['DJANGO_COLORS'] = 'False'


class Command(BaseCommand):
    """
    Example: python manage.py drop corporate_memberships memberships
    """

    def run_sql(self, sql, **options):
        """
        Parse through sql statements.
        Execute each sql statement.
        Commit in one transaction.
        """
        # sql statement regex
        statements = re.compile(r";[ \t]*$", re.M)
        sql_list = []

        # database information
        using = options.get('database', DEFAULT_DB_ALIAS)
        connection = connections[using]

        for statement in statements.split(sql.decode(settings.FILE_CHARSET)):
            # Remove any comments from the file
            statement = re.sub(r"--.*([\n\Z]|$)", "", statement)
            if statement.strip():
                sql_list.append(statement + u";")

        try:
            cursor = connection.cursor()
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
            for sql in sql_list:
                cursor.execute(sql)
            cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
        except Exception as e:
            transaction.rollback_unless_managed()
            raise CommandError("""
                Error running SQL. Possible reasons:
                * The database isn't running or isn't configured correctly.
                * At least one of the database tables doesn't exist.
                * The SQL was invalid.
                The full error: %s""" % (e))
        transaction.commit_unless_managed()

        return sql_list

    def drop_tables(self, app_name, **options):
        """
        Drop application tables
        """
        # get sql --------------
        sql = BytesIO()
        call_command('sqlclear', app_name, stdout=sql)
        sql.seek(0)

        # run sql ---------------
        statements = self.run_sql(sql.read().decode(), **options)
        sql.close()

        return statements

    def handle(self, *app_names, **options):
        """
        Drop application tables
        Ouput sql statement status
        """
        if not app_names:
            print("%s called without apps specified." % __name__, "Sad bear.")

        for app_name in app_names:
            statements = self.drop_tables(app_name, **options)

            if int(options['verbosity']) < 2:
                continue  # skip the rest

            # chatty Kathy --------------
            if statements:
                print("%s: tables dropped" % app_name)
            else:
                print("%s: No tables to drop" % app_name)
