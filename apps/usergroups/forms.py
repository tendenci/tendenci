from django import forms
from models import Group, GroupMembership

class GroupForm(forms.ModelForm):
    emailrecipient = forms.CharField(label="Email Recipient", required=False, max_length=100, 
                                     help_text='Comma Delimited')
    showasoption = forms.BooleanField(initial=1, label="Show Option",
                                      help_text='Display this user group as an option to logged-in users.')
    class Meta:
        model = Group
        fields = ('name',
                  'label',
                  'entity',
                  'type',
                  'emailrecipient',
                  'showasoption',
                  'allowselfadd',
                  'allowselfremove',
                  'description',
                  'allow_anonymous_view',
                  'allow_user_view',
                  'allow_member_view',
                  'allow_anonymous_edit',
                  'allow_user_edit',
                  'allow_member_edit',
                  'autorespond',
                  'autorespondtemplate',
                  'autorespondpriority',
                  'notes',
                  'status',
                  
                  'status_detail',
                  'permissions',
                  )
        exclude = ('members',)
        permissions = (("view_group","Can view group"),)


class GroupMembershipForm(forms.ModelForm):
    
    class Meta:
        model = GroupMembership
        #exclude = ('group',)