from django import forms
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from attornies.models import Attorney

class AttorneyForm(TendenciBaseForm):
    class Meta:
        model = Attorney
        
    bio = forms.CharField(
        required = False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Attorney._meta.app_label,
        'storme_model':Attorney._meta.module_name.lower()}))
    education = forms.CharField(
        required = False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Attorney._meta.app_label,
        'storme_model':Attorney._meta.module_name.lower()}))
    casework = forms.CharField(
        required = False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Attorney._meta.app_label,
        'storme_model':Attorney._meta.module_name.lower()}))
    admissions = forms.CharField(
        required = False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Attorney._meta.app_label,
        'storme_model':Attorney._meta.module_name.lower()}))
    status_detail = forms.ChoiceField(choices=(('active','Active'),('inactive','Inactive')))
    
    def save(self, *args, **kwargs):
        att = super(AttorneyForm, self).save(commit=False)
        if not att.pk:
            att.creator = self.current_user
            att.creator_username = self.current_user.username
            
        att.owner = self.current_user
        att.owner_username = self.current_user.username
        att.save()
        return att
