from django.apps import AppConfig
from django.db.models.signals import post_migrate


class JobsConfig(AppConfig):
    name = 'tendenci.apps.jobs'
    verbose_name = 'Jobs'

    def ready(self):
        super(JobsConfig, self).ready()
        from tendenci.apps.jobs.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
