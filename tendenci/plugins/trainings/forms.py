from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from trainings.models import Training, Completion
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class TrainingForm(TendenciBaseForm):
    class Meta:
        model = Training
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    description = forms.CharField(required=False,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'trainings','storme_model':Training._meta.module_name.lower()}))

class CompletionForm(TendenciBaseForm):
    finish_dt = SplitDateTimeField(label=_('Completion Date/Time'),
        initial=datetime.now())
    class Meta:
        model = Completion
        fields = ('finish_dt', 'feedback', 'allow_anonymous_view')
        fieldsets = [('', {
                'fields': ['finish_dt',
                         'feedback'
                         ]
                }),
                ('Permissions', {
                'fields': ['allow_anonymous_view',
                         'user_perms',
                         'member_perms',
                         'group_perms',
                         ],
                'classes': ['permissions']
                })]

#     def __init__(self, *args, **kwargs):
#         super(CompletionForm, self).__init__(*args, **kwargs)
#         fields_to_pop = [
#             'user_perms',
#             'group_perms',
#             'member_perms',
#             'status',
#             'status_detail'
#         ]
# 
#         for f in list(set(fields_to_pop)):
#             if f in self.fields:
#                 self.fields.pop(f)