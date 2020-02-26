from django.apps import AppConfig
from django.db.models.signals import post_migrate


class NewsConfig(AppConfig):
    name = 'tendenci.apps.news'
    verbose_name = 'News'

    def ready(self):
        super(NewsConfig, self).ready()
        from tendenci.apps.news.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
