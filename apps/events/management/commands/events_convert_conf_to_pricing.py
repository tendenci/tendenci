import re
from django.core.management.base import BaseCommand
from datetime import datetime

class Command(BaseCommand):
    """
    Move data from RegistrationConfiguration to RegConfPricing
    """
    def handle(self, *event_ids, **options):
        from events.models import RegistrationConfiguration
        from events.models import RegConfPricing
        from django.db import connection, transaction

        reg8n_configs = RegistrationConfiguration.objects.all()
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
