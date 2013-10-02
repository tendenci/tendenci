from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """"
    Update group type to be 'system_generated' for the system generated groups.

    Usage: ./manage.py update_system_generated_type
    """

    def handle(self, *args, **options):
        from tendenci.apps.user_groups.models import Group
        from tendenci.addons.memberships.models import MembershipType
        from tendenci.core.site_settings.utils import get_setting

        # membership group ids
        groups_list = list(MembershipType.objects.values_list('group', flat=True))
        # corp reps group id
        reps_group_id = get_setting('module',
                                    'corporate_memberships',
                                    'corpmembershiprepsgroupid')
        if reps_group_id:
            groups_list.append(reps_group_id)

        if groups_list:
            # change type to 'system_generated'
            Group.objects.filter(id__in=groups_list
                                ).update(type='system_generated')
