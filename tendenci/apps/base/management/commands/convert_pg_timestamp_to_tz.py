from __future__ import print_function
from datetime import datetime
from dateutil import tz

from django.core.management.base import BaseCommand
from django.db.models.loading import get_models
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    """
    Loop through all models and update the data for fieldtype
    of timestamp to convert data so it can then be stored as
    timestamptz.

    Usage:
        .manage.py convert_pg_timestamp_to_tz
    """
    def convert_to_utc(self, timestamp):
        from_zone = tz.gettz(settings.TIME_ZONE)
        to_zone = tz.gettz('UTC')

        current = timestamp.replace(tzinfo=from_zone)
        utc = current.astimezone(to_zone)

        return utc

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])

        if "postgresql" in settings.DATABASES['default']['ENGINE']:

            updated_field_count = 0
            total_values_updated = 0
            start_dt = datetime.now()
            print("START: %s" % start_dt)

            models = get_models()
            for model in models:
                # Disable auto_now for this model so we don't affect these
                # fields with this update
                for field in model._meta.fields:
                    if field.name in ['update_dt', 'date_done', 'action_time', 'date_changed']:
                        field.auto_now = False

                for field in model._meta.fields:
                    cursor = connection.cursor()
                    cursor.execute("SELECT relname FROM pg_class WHERE relname = '%s';" % model._meta.db_table)
                    table_exists = cursor.fetchone()
                    if table_exists:
                        cursor = connection.cursor()
                        cursor.execute("SELECT atttypid FROM pg_attribute WHERE attrelid = '%s'::regclass AND attname = '%s';" % (model._meta.db_table, field.name))

                        field_type = cursor.fetchone()
                        if field_type:
                            field_type = field_type[0]

                        # "timestamp without time zone" = 1114
                        # "timestamp with time zone" = 1184

                        if field_type == 1114 and field.db_type(connection=connection) == "timestamp with time zone":

                            print("Updating %s.%s data" % (model._meta.db_table, field.name))
                            print("%s\n" % datetime.now())
                            try:
                                objects = model.objects.all()
                                print(objects)
                                print("%s objects" % objects.count())
                                total_values_updated = total_values_updated + objects.count()
                            except:
                                objects = []

                            if objects:
                                for obj in objects:
                                    try:
                                        val = getattr(obj, field.name)
                                    except:
                                        val = None

                                    if val:
                                        new_val = self.convert_to_utc(val)
                                        if verbosity >= 2:
                                            print("%s %s ID:%s %s -> %s" % (model._meta.verbose_name, field.name, obj.pk, val, new_val))

                                        setattr(obj, field.name, new_val)
                                        try:
                                            obj.save()
                                        except Exception as e:
                                            print("failed to update %s %s" % (model._meta.verbose_name, obj.pk))
                                            print(e)

                            # Change the field type to be 'timestamp with time zone', 1184
                            cursor = connection.cursor()
                            cursor.execute("UPDATE pg_attribute SET atttypid = '1184' WHERE attrelid = '%s'::regclass AND attname = '%s';" % (model._meta.db_table, field.name))
                            print("Finished %s.%s data\n" % (model._meta.db_table, field.name))

                            updated_field_count = updated_field_count + 1

                # Turn auto_now back on for this model
                for field in model._meta.fields:
                    if field.name in ['update_dt', 'date_done', 'action_time', 'date_changed']:
                        field.auto_now = True

            print("FINISH at : %s" % datetime.now())
            print("Started at: %s" % start_dt)
            print("Updated %s timestamp fields to utc with timezone support." % updated_field_count)
            print("Updated %s timestamp values." % total_values_updated)
        else:
            print("This command only runs on Postgresql databases.")
