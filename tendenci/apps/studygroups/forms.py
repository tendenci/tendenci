from django import forms

from tendenci.apps.studygroups.models import StudyGroup, Officer
from tendenci.apps.user_groups.models import GroupMembership, Group
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.base.fields import SplitDateTimeField
from tendenci.apps.base.utils import get_template_list

template_choices = [('default.html','Default')]
template_choices += get_template_list()

class StudyGroupForm(TendenciBaseForm):
    mission = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':StudyGroup._meta.app_label, 
        'storme_model':StudyGroup._meta.model_name.lower()}))
    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':StudyGroup._meta.app_label, 
        'storme_model':StudyGroup._meta.model_name.lower()}))
    notes = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':StudyGroup._meta.app_label, 
        'storme_model':StudyGroup._meta.model_name.lower()}))
        
    class Meta:
        model = StudyGroup
        fields = (
        'title',
        'slug',
        'group',
        'mission',
        'content',
        'notes',
        'contact_name',
        'contact_email',
        'join_link',
        'tags',
        'allow_anonymous_view',
        'syndicate',
        'status_detail',
        )
        fieldsets = [('Study Group Information', {
                      'fields': ['title',
                                 'slug',
                                 'group',
                                 'mission',
                                 'content',
                                 'notes',
                                 'contact_name',
                                 'contact_email',
                                 'join_link',
                                 'tags'
                                 ],
                      'legend': '',
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['syndicate',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))

    def __init__(self, *args, **kwargs): 
        super(StudyGroupForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['mission'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['notes'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['mission'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['notes'].widget.mce_attrs['app_instance_id'] = 0


class StudyGroupAdminForm(TendenciBaseForm):
    mission = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':StudyGroup._meta.app_label, 
        'storme_model':StudyGroup._meta.model_name.lower()}))
    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':StudyGroup._meta.app_label, 
        'storme_model':StudyGroup._meta.model_name.lower()}))
    notes = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':StudyGroup._meta.app_label, 
        'storme_model':StudyGroup._meta.model_name.lower()}))

    group = forms.ModelChoiceField(required=False, queryset=Group.objects.filter(status=True, status_detail="active").order_by('name'))

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

    class Meta:
        model = StudyGroup
        
        fields = (
        'title',
        'slug',
        'group',
        'mission',
        'content',
        'notes',
        'contact_name',
        'contact_email',
        'join_link',
        'tags',
        'allow_anonymous_view',
        'syndicate',
        'status_detail',
        )
        
    def __init__(self, *args, **kwargs): 
        super(StudyGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['mission'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['notes'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['mission'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['notes'].widget.mce_attrs['app_instance_id'] = 0


class StudyGroupAdminChangelistForm(TendenciBaseForm):
    group = forms.ModelChoiceField(required=True, queryset=Group.objects.filter(status=True, status_detail="active").order_by('name'))

    class Meta:
        model = StudyGroup

        fields = (
        'title',
        'group',
        )


class OfficerForm(forms.ModelForm):
    #user = forms.ChoiceField(choices=[])
	
    class Meta:
        model = Officer
        exclude = ('study_group',)

    def __init__(self, study_group_group, *args, **kwargs):
        super(OfficerForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['position', 'user', 'phone']
        # Initialize user.  Label depends on nullability.
        # Priority
        # 1. fullname
        # 2. username
        # 3. email
        group_members = []
        if study_group_group:
            group_members = GroupMembership.objects.filter(group=study_group_group).select_related()
        choices = [('', '---------')]
        for m in group_members:
            u = m.member
            label = ''
            if u.first_name and u.last_name:
                label = u.first_name + ' ' + u.last_name
            elif u.username:
                label = u.username
            elif u.email:
                label = u.email
            if len(label) > 23:
                label = label[0:20] + '...'
            choices.append((u.pk, label))
        self.fields['user'].choices = choices
        self.fields['user'].widget.attrs['class'] = 'officer-user'
