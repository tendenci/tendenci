from django.apps import AppConfig


class EntitiesConfig(AppConfig):
    name = 'tendenci.apps.entities'
    verbose_name = 'Entities'

    def ready(self):
        super(EntitiesConfig, self).ready()
