from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CorporateMembershipsConfig(AppConfig):
    name = 'tendenci.apps.corporate_memberships'
    verbose_name = 'Corporate Memberships Application'

    def ready(self):
        super(CorporateMembershipsConfig, self).ready()
        from tendenci.apps.corporate_memberships.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
