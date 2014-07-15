from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Update corporate membership representatives group
        1) Create the group if not already exists,
            and add a setting corpmembershiprepsgroupid and
            store the group id to the setting
        2) Loop through corp reps and add reps to the group.
        3) Remove the non-rep users from the group.

    Usage: python manage.py clean_corporate_memberships
    """
    def handle(self, *args, **kwargs):
        from tendenci.core.site_settings.models import Setting
        from tendenci.apps.user_groups.models import Group, GroupMembership
        from tendenci.addons.corporate_memberships.models import CorpMembershipRep
        verbosity = int(kwargs['verbosity'])

        cmrg_setting, created = Setting.objects.get_or_create(
                        name='corpmembershiprepsgroupid')
        description = 'This Group is for all corporate membership representatives. ' + \
                    'Adding or deleting a representative will automatically ' + \
                    'add (or remove) the user to (or from) this group.'
        if created:
            cmrg_setting.label = 'Corporate Membership Representatives Group Id'
            cmrg_setting.description = description
            cmrg_setting.data_type = 'int'
            cmrg_setting.value = '0'
            cmrg_setting.default_value = '0'
            cmrg_setting.input_type = 'text'
            cmrg_setting.input_value = ''
            cmrg_setting.client_editable = False
            cmrg_setting.store = True
            cmrg_setting.scope = 'module'
            cmrg_setting.scope_category = 'corporate_memberships'
            cmrg_setting.save()

        group = None
        group_id = int(cmrg_setting.value)
        if group_id:
            [group] = Group.objects.filter(id=group_id)[:1] or [None]

        if not group:
            # first check if we have a default group. if not, create one
            # so that this reps group won't become the one with id=1
            Group.objects.get_or_create_default()

            group = Group(
                      name='Corporate Membership Representatives',
                      slug='corporate-membership-representatives',
                      label='Corporate Membership Representatives',
                      type='system_generated',
                      show_as_option=False,
                      allow_self_add=False,
                      allow_self_remove=False,
                      description=description,
                      allow_anonymous_view=False,
                      allow_user_view=False,
                      allow_member_view=False,
                      allow_user_edit=False,
                      allow_member_edit=False)
            group.save()
            cmrg_setting.value = str(group.id)
            cmrg_setting.save()
        else:
            # remove all non-reps from group
            for user in group.members.all():
                if not CorpMembershipRep.objects.filter(user=user).exists():
                    if verbosity >= 2:
                        print('Removing user "%s" from group' % user.username)
                    gm = GroupMembership.objects.get(group=group,
                                                 member=user)
                    gm.delete()

        # add reps to group
        for rep in CorpMembershipRep.objects.all():
            user = rep.user
            if not group.is_member(user):
                if verbosity >= 2:
                    print('Adding user "%s" to group' % user.username)
                group.add_user(user)


