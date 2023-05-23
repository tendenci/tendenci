from django.apps import AppConfig


class TrainingsConfig(AppConfig):
    name = 'tendenci.apps.trainings'
    verbose_name = 'Trainings'

    def ready(self):
        super(TrainingsConfig, self).ready()
        from .signals import init_signals
        init_signals()
