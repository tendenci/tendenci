from django.apps import AppConfig
from django.db.models.signals import post_migrate


class VideosConfig(AppConfig):
    name = 'tendenci.apps.videos'
    verbose_name = 'Videos'

    def ready(self):
        super(VideosConfig, self).ready()
        from tendenci.apps.videos.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
