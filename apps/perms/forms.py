from os.path import join
from django.conf import settings
from perms.fields import GroupPermissionField, groups_with_perms
from perms.fields import UserPermissionField, user_perm_bits
from form_utils.forms import BetterModelForm

class TendenciBaseForm(BetterModelForm):
    """
        Base form that adds user permission fields
    """
    group_perms = GroupPermissionField() 
    user_perms = UserPermissionField() 
        
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
            value = (False,False)
                                
        return value
    
    def clean_group_perms(self):
        value = self.cleaned_data['group_perms']
        groups_and_perms = []
        if value:
            for item in value:
                perm, group_pk  = item.split('_')
                groups_and_perms.append((group_pk,perm,))
            value = tuple(groups_and_perms)
        return value
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(TendenciBaseForm, self).__init__(*args, **kwargs)
        
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if 'group_perms' in self.fields:
                self.fields['group_perms'].initial = groups_with_perms(instance)
            if 'user_perms' in self.fields:
                self.fields['user_perms'].initial = user_perm_bits(instance)