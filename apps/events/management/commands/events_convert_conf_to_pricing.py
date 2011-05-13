from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Move data from RegistrationConfiguration to RegConfPricing
    """
    def handle(self, *event_ids, **options):
        from events.models import RegistrationConfiguration
        from events.models import RegConfPricing

        reg8n_configs = RegistrationConfiguration.objects.all()

        for config in reg8n_configs:
            rcp = RegConfPricing()

            rcp.title = ''
            rcp.quantity = 0
            rcp.group = None
            rcp.reg_conf = config

            rcp.early_price = config.early_price
            rcp.regular_price = config.regular_price
            rcp.late_price = config.late_price

            rcp.early_dt = config.early_dt
            rcp.regular_dt = config.regular_dt
            rcp.late_dt = config.late_dt
            rcp.end_dt = config.end_dt

            rcp.save()
