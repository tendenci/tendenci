from django.apps import AppConfig
from django.db.models.signals import post_migrate


class MembershipsConfig(AppConfig):
    name = 'tendenci.apps.memberships'
    verbose_name = 'Memberships Application'

    def ready(self):
        super(MembershipsConfig, self).ready()
        from tendenci.apps.memberships.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
