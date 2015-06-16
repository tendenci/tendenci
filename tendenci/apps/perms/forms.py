from django import forms
from django.utils.translation import ugettext_lazy as _

from form_utils.forms import BetterModelForm

from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.perms.fields import GroupPermissionField, groups_with_perms, UserPermissionField, MemberPermissionField, group_choices


class TendenciBaseForm(FormControlWidgetMixin, BetterModelForm):
    """
    Base form that adds user permission fields
    """
    group_perms = GroupPermissionField()
    user_perms = UserPermissionField()
    member_perms = MemberPermissionField()
    # override due to the changes for BooleanField to NullBooleanField
    allow_anonymous_view = forms.BooleanField(label=_('Public can view'), required=False, initial=True)

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

    def clean_allow_anonymous_view(self):
        data = self.cleaned_data.get('allow_anonymous_view', False)
        if data:
            return True
        else:
            return False

    def __init__(self, *args, **kwargs):
        from tendenci.apps.perms.fields import user_perm_bits, member_perm_bits
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

        instance = kwargs.get('instance', None)
        if instance:
            if 'group_perms' in self.fields:
                self.fields['group_perms'].initial = groups_with_perms(instance)
            if 'user_perms' in self.fields:
                self.fields['user_perms'].initial = user_perm_bits(instance)
            if 'member_perms' in self.fields:
                self.fields['member_perms'].initial = member_perm_bits(instance)
