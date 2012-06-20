from django import forms

from chamberlin_projects.models import Project
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class ProjectForm(TendenciBaseForm):
    class Meta:
        model = Project
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    scope_of_work = forms.CharField(required=False,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'chamberlin_projects','storme_model':Project._meta.module_name.lower()}))
    project_description = forms.CharField(required=False,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'chamberlin_projects','storme_model':Project._meta.module_name.lower()}))
