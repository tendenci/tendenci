from django.apps import AppConfig
from django.db.models.signals import post_migrate, post_save


class ChaptersConfig(AppConfig):
    name = 'tendenci.apps.chapters'
    verbose_name = 'Chapters'

    def ready(self):
        super(ChaptersConfig, self).ready()
        from .signals import create_chapter_membership_notice_types, add_member_to_coord_group
        from tendenci.apps.memberships.models import MembershipDefault
        post_migrate.connect(create_chapter_membership_notice_types, sender=self)
        post_save.connect(add_member_to_coord_group, sender=MembershipDefault, weak=False)
