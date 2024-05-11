from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ProjectsConfig(AppConfig):
    name = 'tendenci.apps.projects'
    verbose_name = 'Projects'

    def ready(self):
        super(ProjectsConfig, self).ready()
        from tendenci.apps.projects.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
