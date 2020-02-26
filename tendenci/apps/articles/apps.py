from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ArticlesConfig(AppConfig):
    name = 'tendenci.apps.articles'
    verbose_name = 'Articles'

    def ready(self):
        super(ArticlesConfig, self).ready()
        from tendenci.apps.articles.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
