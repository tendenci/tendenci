from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UserGroupsConfig(AppConfig):
    name = 'tendenci.apps.user_groups'
    verbose_name = 'User Groups'

    def ready(self):
        super(UserGroupsConfig, self).ready()
        from tendenci.apps.user_groups.signals import init_signals, create_notice_types
        init_signals()
        post_migrate.connect(create_notice_types, sender=self)
