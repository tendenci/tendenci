from django.apps import AppConfig
from django.db.models.signals import post_migrate


class HelpFilesConfig(AppConfig):
    name = 'tendenci.apps.help_files'
    verbose_name = 'Help Files'

    def ready(self):
        super(HelpFilesConfig, self).ready()
        from tendenci.apps.help_files.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
