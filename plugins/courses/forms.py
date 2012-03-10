import calendar
from datetime import datetime, timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _

from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField
from perms.forms import TendenciBaseForm

from courses.models import Course, Question, CourseAttempt

class CourseForm(TendenciBaseForm):
    now = datetime.now()
    dd_year = now.year + 1
    dd_month = now.month
    dd_day = now.day
    
    if dd_month == 2 and dd_day == 29:
        # check if next year is a leap year
        if not calendar.isleap(dd_year):
            dd_month = 3
            dd_day = 1
    
    STATUS_CHOICES = (('active','Active'),('pending','Pending'))
    
    status = forms.BooleanField(required=False, initial=False)
    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)
    content = forms.CharField(
                    required=False,
                    widget=TinyMCE(attrs={'style':'width:100%'},
                    mce_attrs={'storme_app_label':u'courses',
                    'storme_model':Course._meta.module_name.lower()}))
    deadline = SplitDateTimeField(
                    required=False,
                    label=_('Deadline'),
                    initial=datetime(year=dd_year, month=dd_month, day=dd_day))
    
    class Meta:
        model = Course
        fields = (
            'title', 
            'content',
            'retries',
            'retry_interval',
            'passing_score',
            'deadline',
            'close_after_deadline',
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
                    'close_after_deadline',
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
        fields = ('number', 'question', 'point_value')
        
    def clean_point_value(self):
        data = self.cleaned_data['point_value']
        if data <= 0:
            raise forms.ValidationError("Point Value should be a positive integer")
        return data

class AnswerForm(forms.Form):
    """
    Create a form based on a given question
    """
    
    def __init__(self, *args, **kwargs):
        """
        Create the answer field based on the question
        """
        self.question = kwargs.pop('question')
        
        # set up answer choices
        choices = []
        for choice in self.question.answers.all():
            choices.append((choice.pk, choice.answer))
            
        self.answers = self.question.correct_answers()
        label = "%s. %s" % (self.question.number, self.question.question)
        
        super(AnswerForm, self).__init__(*args, **kwargs)
        
        if self.answers.count() == 1:
            self.fields['answer'] = forms.ChoiceField(
                label=label,
                choices=choices,
                widget=forms.RadioSelect,
            )
        else:
            self.fields['answer'] = forms.MultipleChoiceField(
                label=label,
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
            )
    
    def points(self):
        """
        Return question's point value if answer is correct.
        Return 0 otherwise.
        """
        if self.is_valid():
            data = self.cleaned_data['answer']
            if self.answers.count() == 1:
                if self.question.answers.filter(pk=data).exists():
                    return self.question.point_value
            else:
                if set(data) == set(self.answers):
                    return self.question.point_value
        return 0

class CourseAttemptForm(forms.ModelForm):
    class Meta:
        model = CourseAttempt
        
class DateRangeForm(forms.Form):
    start_dt = forms.DateField(label=_('Start Date'), initial=datetime.now()-timedelta(days=30), widget=forms.extras.SelectDateWidget)
    end_dt = forms.DateField(label=_('End Date'), initial=datetime.now(), widget=forms.extras.SelectDateWidget)
