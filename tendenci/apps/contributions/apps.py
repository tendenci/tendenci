from django.apps import AppConfig


class ContributionsConfig(AppConfig):
    name = 'tendenci.apps.contributions'
    verbose_name = 'Contributions'

    def ready(self):
        super(ContributionsConfig, self).ready()
