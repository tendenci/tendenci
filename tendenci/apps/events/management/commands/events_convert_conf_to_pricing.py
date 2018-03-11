import re
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Move data from RegistrationConfiguration to RegConfPricing
    """
    def handle(self, *event_ids, **options):
        from tendenci.apps.events.models import RegistrationConfiguration
        from tendenci.apps.events.models import RegConfPricing
        from tendenci.apps.events.models import Registration
        from django.db import connection, transaction

        select_sql = "SELECT * FROM events_registrationconfiguration"
        reg8n_configs = RegistrationConfiguration.objects.raw(select_sql)
        cursor = connection.cursor()

        # add the pricing and update registrations
        for config in reg8n_configs:
            reg_conf_pricing = RegConfPricing()
            reg_conf_pricing.title = ''
            reg_conf_pricing.quantity = 1
            reg_conf_pricing.group_id = None
            reg_conf_pricing.reg_conf_id = config.pk
            reg_conf_pricing.early_price = config.early_price
            reg_conf_pricing.regular_price = config.regular_price
            reg_conf_pricing.late_price = config.late_price
            reg_conf_pricing.early_dt = config.early_dt
            reg_conf_pricing.regular_dt = config.regular_dt
            reg_conf_pricing.late_dt = config.late_dt
            reg_conf_pricing.end_dt = config.end_dt
            reg_conf_pricing.allow_anonymous = True
            reg_conf_pricing.allow_user = False
            reg_conf_pricing.allow_member = False

            reg_conf_pricing.save()

            try:
                # update the registrations with pricing
                registrations = Registration.objects.filter(
                    event=config.event
                )
            #except ObjectDoesNotExist:
            except:
                registrations = []

            for registration in registrations:
                disable_fk_sql = "SET FOREIGN_KEY_CHECKS=0;"
                enable_fk_sql = "SET FOREIGN_KEY_CHECKS=1;"
                update_sql = """
                UPDATE events_registration
                SET reg_conf_price_id = %s
                WHERE id = %s;
                """
                # clean up the pretty sql to a
                # usable statements
                pattern = re.compile(r'[\s\t]+')
                update_sql = update_sql.replace('\n',' ')
                update_sql = re.sub(pattern, ' ', update_sql)

                cursor.execute(disable_fk_sql)
                cursor.execute(update_sql, [reg_conf_pricing.pk, registration.pk])
                cursor.execute(enable_fk_sql)

                transaction.commit_unless_managed()
