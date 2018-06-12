from django import forms

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.case_studies.models import CaseStudy, Image
# from tendenci.apps.files.models import File
from tendenci.libs.tinymce.widgets import TinyMCE

class CaseStudyForm(TendenciBaseForm):
    overview = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':CaseStudy._meta.app_label,
        'storme_model':CaseStudy._meta.model_name.lower()}))

    execution = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':CaseStudy._meta.app_label,
        'storme_model':CaseStudy._meta.model_name.lower()}))

    results = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':CaseStudy._meta.app_label,
        'storme_model':CaseStudy._meta.model_name.lower()}))

    status_detail = forms.ChoiceField(choices=(('active','Active'),('inactive','Inactive')))

    def __init__(self, *args, **kwargs):
        super(CaseStudyForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['overview'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['execution'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['results'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['overview'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['execution'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['results'].widget.mce_attrs['app_instance_id'] = 0

    class Meta:
        model = CaseStudy
        fields = (
            'client',
            'slug',
            'overview',
            'execution',
            'results',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status_detail',
        )

class FileForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = (
            'file',
            'description',
            'file_type',
            'position',
        )

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
