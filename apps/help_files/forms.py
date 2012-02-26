from django import forms
from django.forms import widgets

from models import Request, HelpFile, Topic
from tinymce.widgets import TinyMCE
from captcha.fields import CaptchaField
from perms.forms import TendenciBaseForm
from perms.utils import is_admin
   
class RequestForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = Request

class HelpFileAdminForm(TendenciBaseForm):
    answer = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':HelpFile._meta.app_label, 
        'storme_model':HelpFile._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(choices=(('draft','Draft'),('active','Active')))
    
    class Meta:
        model = HelpFile

    def __init__(self, *args, **kwargs): 
        super(HelpFileAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = 0


class HelpFileForm(TendenciBaseForm):
    answer = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':HelpFile._meta.app_label, 
        'storme_model':HelpFile._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(
        choices=(('draft','Draft'),('active','Active')))

    #topics = forms.MultipleChoiceField(required=True, widget=widgets.CheckboxSelectMultiple())

    class Meta:
        model = HelpFile
        fields = (
            'question',
            'slug',
            'answer',
            'level',
            'topics',
            'is_faq',
            'is_featured',
            'is_video',
            'syndicate',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [('Help File Information', {
                      'fields': ['question',
                                 'slug',
                                 'answer',
                                 'level',
                                 'topics',
                                 ],
                      'legend': ''
                      }),
                      ('Flags', {
                      'fields': ['is_faq',
                                 'is_featured',
                                 'is_video',
                                 ],
                        'classes': ['flags'],
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['syndicate',
                                 'status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(HelpFileForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = 0

        if not is_admin(self.user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
            if 'allow_anonymous_view' in self.fields: self.fields.pop('allow_anonymous_view')
            if 'user_perms' in self.fields: self.fields.pop('user_perms')
            if 'member_perms' in self.fields: self.fields.pop('member_perms')
            if 'group_perms' in self.fields: self.fields.pop('group_perms')
            if 'syndicate' in self.fields: self.fields.pop('syndicate')
