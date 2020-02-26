from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ResumesConfig(AppConfig):
    name = 'tendenci.apps.resumes'
    verbose_name = 'Resumes'

    def ready(self):
        super(ResumesConfig, self).ready()
        from tendenci.apps.resumes.signals import init_signals, create_notice_types
        post_migrate.connect(create_notice_types, sender=self)
