from django import forms
from tendenci.core.perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from tendenci.apps.attorneys.models import Attorney, Photo

class AttorneyForm(TendenciBaseForm):
    class Meta:
        model = Attorney
        fields = (
            'first_name',
            'middle_initial',
            'last_name',
            'slug',
            'category',
            'position',
            'address',
            'address2',
            'city',
            'state',
            'zip',
            'phone',
            'fax',
            'email',
            'bio',
            'education',
            'casework',
            'admissions',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )
        
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

class PhotoForm(TendenciBaseForm):
    class Meta:
        model = Photo
        fields = ('file',)
