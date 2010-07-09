from django import forms
from django.contrib.auth.models import User
from user_groups.models import Group, GroupMembership

# this is the list of apps whose permissions will be displayed on the permission edit page
APPS = ['profiles', 'user_groups', 'articles', 
        'news', 'pages', 'jobs', 'locations', 
        'stories', 'actions']

class GroupForm(forms.ModelForm):
    email_recipient = forms.CharField(label="Email Recipient", required=False, max_length=100, 
                                     help_text='Comma Delimited')
    show_as_option = forms.BooleanField(initial=1, label="Show Option",
                                      help_text='Display this user group as an option to logged-in users.')
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
                  'allow_anonymous_view',
                  'allow_user_view',
                  'allow_member_view',
                  'allow_anonymous_edit',
                  'allow_user_edit',
                  'allow_member_edit',
                  'auto_respond',
                  'auto_respond_template',
                  'auto_respond_priority',
                  'notes',
                  'status',
                  
                  'status_detail',
                  )
        exclude = ('members',)
       

class GroupMembershipForm(forms.ModelForm):
    def __init__(self, mygroup=None, user_id=None, *args, **kwargs):
        super(GroupMembershipForm, self).__init__(*args, **kwargs)
        self.fields['member'].queryset = User.objects.filter(is_active=1)
        if mygroup:
            # exclude those already joined
            exclude_userid = [user.id for user in mygroup.members.all()]
            self.fields['member'].queryset = User.objects.all().exclude(id__in=exclude_userid)
        else:
            self.fields['member'].queryset = User.objects.all()
        if user_id:
            del self.fields["member"]
            
        
    class Meta:
        model = GroupMembership
        exclude = ('group',)
        
class GroupPermissionForm(forms.ModelForm):
    class Meta:
        model = Group
        fields= ('permissions',)
        
    def __init__(self, *args, **kwargs):
        super(GroupPermissionForm, self).__init__(*args, **kwargs)
        # filter out the unwanted permissions,
        # only display the permissions for the apps in APPS
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission
        content_types = ContentType.objects.filter(app_label__in=APPS)
        
        self.fields['permissions'].queryset = Permission.objects.filter(content_type__in=content_types)
        