from django import forms
from django.utils.translation import ugettext_lazy as _

from projects.models import Project, Presentation, Report, Article, Picture
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class ProjectForm(TendenciBaseForm):
    class Meta:
        model = Project
        fields = (
            'title',
            'slug',
            'project_name',
            'program',
            'program_year',
            'project_number',
            'project_status',
            'principal_investigator',
            'principal_investigator_company',
            'participants',
            'rpsea_pm',
            'start_dt',
            'end_dt',
            'project_abstract',
            'project_abstract_date',
            'project_fact_sheet_title',
            'project_fact_sheet_url',
            'website_title',
            'website_url',
            'article_title',
            'article_url',
            'project_objectives',
            'video_embed_code',
            'video_title',
            'video_description',
            'access_type',
            'research_category',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status',
            'status_detail',
        )
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    project_objectives = forms.CharField(required=True,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'projects','storme_model':Project._meta.module_name.lower()}))
    video_description = forms.CharField(required=True,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'projects','storme_model':Project._meta.module_name.lower()}))
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['project_objectives'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['video_description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['project_objectives'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['video_description'].widget.mce_attrs['app_instance_id'] = 0

class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ['title', 'presentation_dt', 'file']
    
    def __init__(self, *args, **kwargs):
        super(PresentationForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("File")
        
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['type', 'other', 'report_dt', 'file']
    
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("File")
        
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['article_dt', 'file']
    
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("File")

class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['file']
        
    def __init__(self, *args, **kwargs):
        super(PictureForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Photo")
