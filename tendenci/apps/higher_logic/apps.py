from django.apps import AppConfig


class Higher_LogicConfig(AppConfig):
    name = 'tendenci.apps.higher_logic'
    verbose_name = 'Higher Logic'

    def ready(self):
        super(Higher_LogicConfig, self).ready()
        from .signals import init_signals
        init_signals()
