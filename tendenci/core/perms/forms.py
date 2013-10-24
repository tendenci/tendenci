from tendenci.core.perms.fields import GroupPermissionField, groups_with_perms, UserPermissionField, MemberPermissionField, group_choices
from form_utils.forms import BetterModelForm


class TendenciBaseForm(BetterModelForm):
    """
    Base form that adds user permission fields
    """
    group_perms = GroupPermissionField()
    user_perms = UserPermissionField()
    member_perms = MemberPermissionField()

    def clean_user_perms(self):
        user_perm_bits = []
        value = self.cleaned_data['user_perms']
        if value:
            if 'allow_user_view' in value:
                user_perm_bits.append(True)
            else:
                user_perm_bits.append(False)

            if 'allow_user_edit' in value:
                user_perm_bits.append(True)
            else:
                user_perm_bits.append(False)
            value = tuple(user_perm_bits)
        else:
            value = (False, False,)
        return value

    def clean_member_perms(self):
        member_perm_bits = []
        value = self.cleaned_data['member_perms']
        if value:
            if 'allow_member_view' in value:
                member_perm_bits.append(True)
            else:
                member_perm_bits.append(False)

            if 'allow_member_edit' in value:
                member_perm_bits.append(True)
            else:
                member_perm_bits.append(False)
            value = tuple(member_perm_bits)
        else:
            value = (False, False,)
        return value

    def clean_group_perms(self):
        value = self.cleaned_data['group_perms']
        groups_and_perms = []
        if value:
            for item in value:
                perm, group_pk = item.split('_')
                groups_and_perms.append((group_pk, perm,))
            value = tuple(groups_and_perms)
        return value

    def __init__(self, *args, **kwargs):
        from tendenci.core.perms.fields import user_perm_bits, member_perm_bits
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            if not hasattr(self, 'user'):
                self.user = None

        super(TendenciBaseForm, self).__init__(*args, **kwargs)

        # needs to update the choices on every pull
        # in case groups get added
        if 'group_perms' in self.fields:
            self.fields['group_perms'].choices = group_choices()

        if 'instance' in kwargs:
            instance = kwargs['instance']
            if 'group_perms' in self.fields:
                self.fields['group_perms'].initial = groups_with_perms(instance)
            if 'user_perms' in self.fields:
                self.fields['user_perms'].initial = user_perm_bits(instance)
            if 'member_perms' in self.fields:
                self.fields['member_perms'].initial = member_perm_bits(instance)
