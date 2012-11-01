from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Look at the membership protection setting and update
    each membership accordingly.
    """
    def handle(self, *args, **kwargs):
        from tendenci.core.site_settings.utils import get_setting
        from tendenci.addons.memberships.models import Membership
        from tendenci.apps.user_groups.models import GroupMembership
        protection = get_setting('module', 'memberships', 'memberprotection')

        if protection == 'public':
            Membership.objects.update(
                allow_anonymous_view=True,
                allow_user_view=False,
                allow_member_view=False
            )
        elif protection == 'all-members':
            Membership.objects.update(
                allow_anonymous_view=False,
                allow_user_view=False,
                allow_member_view=True
            )
        elif protection == 'member-type':
            Membership.objects.update(
                allow_anonymous_view=False,
                allow_user_view=False,
                allow_member_view=False
            )
            for membership in Membership.objects.all():

                # add or remove from group -----
                if membership.is_active():  # should be in group; make sure they're in
                    membership.membership_type.group.add_user(membership.user)
                else:  # should not be in group; make sure they're out
                    GroupMembership.objects.filter(
                        member=membership.user,
                        group=membership.membership_type.group
                    ).delete()
                # -----

                print membership

        else:  # private
            Membership.objects.update(
                allow_anonymous_view=False,
                allow_user_view=False,
                allow_member_view=False
            )
