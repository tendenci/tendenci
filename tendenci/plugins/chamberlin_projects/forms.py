from django import forms

from chamberlin_projects.models import Project
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from tendenci.apps.base.fields import SplitDateTimeField

class ProjectForm(TendenciBaseForm):
    class Meta:
        model = Project  
        fields = (
            'title',
            'slug',
            'location',
            'city',
            'state',
            'construction_type',
            'construction_activity',
            'category',
            'contract_amount',
            'owner_name',
            'architect',
            'general_contractor',
            'scope_of_work',
            'project_description',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    scope_of_work = forms.CharField(required=False,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'chamberlin_projects','storme_model':Project._meta.module_name.lower()}))
    project_description = forms.CharField(required=False,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'chamberlin_projects','storme_model':Project._meta.module_name.lower()}))

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['scope_of_work'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['project_description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['scope_of_work'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['project_description'].widget.mce_attrs['app_instance_id'] = 0
