from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    example: python manage.py events_init_end_dt
    """
    def handle(self, *event_ids, **options):
        from tendenci.addons.events.models import RegistrationConfiguration
        reg8n_configs = RegistrationConfiguration.objects.all()

        for config in reg8n_configs:
            config.end_dt = config.late_dt
            config.save()

