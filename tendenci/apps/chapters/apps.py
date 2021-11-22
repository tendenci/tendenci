from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ChaptersConfig(AppConfig):
    name = 'tendenci.apps.chapters'
    verbose_name = 'Chapters'

    def ready(self):
        super(ChaptersConfig, self).ready()
        from .signals import create_chapter_membership_notice_types
        post_migrate.connect(create_chapter_membership_notice_types, sender=self)
