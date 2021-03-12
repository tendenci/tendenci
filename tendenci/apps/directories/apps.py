from django.apps import AppConfig
from django.db.models.signals import post_migrate


class DirectoriesConfig(AppConfig):
    name = 'tendenci.apps.directories'
    verbose_name = 'Directories'

    def ready(self):
        super(DirectoriesConfig, self).ready()
        from tendenci.apps.directories.affiliates import models
        from tendenci.apps.directories.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
