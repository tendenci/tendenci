from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from courses.models import Course, Question
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class CourseForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    content = forms.CharField(required=True,
                widget=TinyMCE(attrs={'style':'width:100%'},
                mce_attrs={'storme_app_label':u'courses',
                'storme_model':Course._meta.module_name.lower()}))
    deadline = SplitDateTimeField(label=_('Deadline'), initial=datetime.now())
                
    class Meta:
        model = Course
        fields = (
            'title', 
            'content',
            'retries',
            'retry_interval',
            'passing_score',
            'deadline',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )
        fieldsets = [
            ('Course Information', {
                'fields': [
                    'title',
                    'content',
                    'retries',
                    'retry_interval',
                    'passing_score',
                    'deadline',
                    'tags',
                    ],
                'legend': ''
            }),
            ('Permissions', {
                'fields': [
                    'allow_anonymous_view',
                    'user_perms',
                    'member_perms',
                    'group_perms',
                    ],
                'classes': ['permissions'],
            }),
            ('Administrator Only', {
                'fields': [
                    'status',
                    'status_detail'], 
                'classes': ['admin-only'],
            })]
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('question', 'answer_choices', 'answer', 'point_value')
        
    
