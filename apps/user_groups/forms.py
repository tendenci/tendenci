from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from user_groups.models import Group, GroupMembership
from user_groups.utils import member_choices
from perms.forms import TendenciBaseForm
from perms.utils import is_admin


class GroupAdminForm(TendenciBaseForm):
    email_recipient = forms.CharField(label="Recipient Email", required=False, max_length=100, 
        help_text='Recipient email(s), comma delimited') 
    show_as_option = forms.BooleanField(initial=1, label="Show Option", 
        help_text='Display this user group as an option to logged-in users.',required=False)

    class Meta:
        model = Group
        fields = ('name',
          'label',
          'entity',
          'type',
          'email_recipient',
          'show_as_option',
          'allow_self_add',
          'allow_self_remove',
          'description',
          'auto_respond',
          'auto_respond_template',
          'auto_respond_priority',
          'notes',
          'allow_anonymous_view',
          'members',
          'permissions',
          'user_perms',
          'status',
          'status_detail',
          )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)   
        # filter out the unwanted permissions,
        content_types = ContentType.objects.exclude(app_label='auth') 
        self.fields['permissions'].queryset = Permission.objects.filter(content_type__in=content_types)  
       
class GroupForm(TendenciBaseForm):
    STATUS_CHOICES = (('active','Active'),('inactive','Inactive'),)
    email_recipient = forms.CharField(label="Recipient Email", required=False, max_length=100, 
        help_text='Recipient email(s), comma delimited')
    show_as_option = forms.BooleanField(initial=1, label="Show Option", 
        help_text='Display this group as an option to logged-in users.',required=False)
    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = Group
        fields = ('name',
                  'label',
                  'entity',
                  'type',
                  'email_recipient',
                  'show_as_option',
                  'allow_self_add',
                  'allow_self_remove',
                  'description',
                  'auto_respond',
                  'auto_respond_template',
                  'auto_respond_priority',
                  'notes',
                  'allow_anonymous_view',
                  'user_perms',
                  'status',
                  'status_detail',
                  )
        exclude = ('members','group_perms')

        fieldsets = [('Group Information', {
                      'fields': ['name',
                                 'label',
                                 # 'entity',
                                 'email_recipient',
                                 'show_as_option',
                                 'allow_self_add', 
                                 'allow_self_remove',
                                 'description'
                                 'auto_respond',
                                 'auto_respond_template',
                                 'auto_respond_priority'
                                 ],
                      'legend': ''
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        if not is_admin(self.user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')               

class GroupMembershipForm(forms.ModelForm):
    def __init__(self, group=None, user_id=None, *args, **kwargs):
        super(GroupMembershipForm, self).__init__(*args, **kwargs)        
        if group:
            # exclude those already joined
            exclude_userid = [user.id for user in group.members.all()]
            self.fields['member'].queryset = User.objects.filter(is_active=1).exclude(id__in=exclude_userid)
        else:
            self.fields['member'].queryset = User.objects.filter(is_active=1)
        if user_id:
            del self.fields["member"]
            
        
    class Meta:
        model = GroupMembership
        exclude = ('group',)
        
class GroupMembershipBulkForm(forms.Form):
    def __init__(self, group, *args, **kwargs):
        member_label = kwargs.pop('member_label', 'username')
        super(GroupMembershipBulkForm, self).__init__(*args, **kwargs)
        self.fields['members'].initial = group.members.all()
        self.fields['members'].choices = member_choices(group, member_label)
    
    members = forms.ModelMultipleChoiceField(queryset = User.objects.filter(is_active=1), required=False)
    role = forms.CharField(required=False, max_length=255)
    status = forms.BooleanField(required=False, initial=True)
    status_detail = forms.ChoiceField(choices=(('active','Active'), ('inactive','Inactive'),), initial='active')
        
class GroupPermissionForm(forms.ModelForm):
    class Meta:
        model = Group
        fields= ('permissions',)
        
    def __init__(self, *args, **kwargs):
        super(GroupPermissionForm, self).__init__(*args, **kwargs)
        # filter out the unwanted permissions,
        # only display the permissions for the apps in APPS
        content_types = ContentType.objects.exclude(app_label='auth')
        
        self.fields['permissions'].queryset = Permission.objects.filter(content_type__in=content_types)
        
class GroupMembershipEditForm(forms.ModelForm):
    class Meta:
        model = GroupMembership
        fields = ('role', 'status', 'status_detail')
