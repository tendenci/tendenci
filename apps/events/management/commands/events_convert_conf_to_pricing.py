import re
from django.core.management.base import BaseCommand
from django.db import models
from datetime import datetime


class DummyRegistrationConfiguration(models.Model):
    payment_method_id = models.IntegerField()

    early_price = models.DecimalField(max_digits=21, decimal_places=2, default=0)
    regular_price = models.DecimalField(max_digits=21, decimal_places=2, default=0)
    late_price = models.DecimalField(max_digits=21, decimal_places=2, default=0)

    early_dt = models.DateTimeField()
    regular_dt = models.DateTimeField()
    late_dt = models.DateTimeField()
    end_dt = models.DateTimeField(default=0)

    payment_required = models.BooleanField()

    limit = models.IntegerField(default=0)
    enabled = models.BooleanField(default=False)

    is_guest_price = models.BooleanField()

    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)


class Command(BaseCommand):
    """
    Move data from RegistrationConfiguration to RegConfPricing
    """
    def handle(self, *event_ids, **options):
        from events.models import RegistrationConfiguration
        from events.models import RegConfPricing
        from django.db import connection, transaction

        select_sql = "SELECT * FROM events_registrationconfiguration"
        reg8n_configs = DummyRegistrationConfiguration.objects.raw(select_sql)
        cursor = connection.cursor()

        for config in reg8n_configs:
            insert_sql = """
            INSERT INTO events_regconfpricing (
                title, 
                quantity, 
                group_id, 
                reg_conf_id, 
                early_price, 
                regular_price,
                late_price,
                early_dt,
                regular_dt,
                late_dt,
                end_dt
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            # clean up the pretty sql to a 
            # usable statements
            pattern = re.compile(r'[\s\t]+')
            insert_sql = insert_sql.replace('\n',' ')
            insert_sql = re.sub(pattern, ' ', insert_sql)

            cursor.execute(insert_sql, [
                '',
                1,
                None,
                config.pk,
                config.early_price,
                config.regular_price,
                config.late_price,
                config.early_dt,
                config.regular_dt,
                config.late_dt,
                config.end_dt
            ])

            transaction.commit_unless_managed()
