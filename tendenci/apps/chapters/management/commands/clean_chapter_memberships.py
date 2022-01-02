from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Set the status detail of the chapter membership to expired.
    Remove the user from the chapter group.
    Usage: python manage.py clean_chapter_memberships
    """
    def handle(self, *args, **kwargs):
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from tendenci.apps.chapters.models import ChapterMembership, ChapterMembershipType
        from tendenci.apps.user_groups.models import GroupMembership

        for membership_type in ChapterMembershipType.objects.all():
            grace_period = membership_type.expiration_grace_period

            # get expired memberships out of grace period
            chapter_memberships = ChapterMembership.objects.filter(
                membership_type=membership_type,
                expire_dt__lt=datetime.now() - relativedelta(days=grace_period),
                status=True).filter(status_detail='active')

            for m in chapter_memberships:
                m.status_detail = 'expired'
                m.save()

                # remove from chapter group
                GroupMembership.objects.filter(
                    member=m.user,
                    group=m.chapter.group
                ).delete()
