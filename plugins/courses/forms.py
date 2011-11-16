from django import forms

from courses.models import Course
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class CourseForm(TendenciBaseForm):
    class Meta:
        model = Course
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    content = forms.CharField(required=True,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'courses','storme_model':Course._meta.module_name.lower()}))
