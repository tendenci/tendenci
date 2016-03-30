from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.help_files.models import Request, HelpFile, Topic
from tendenci.libs.tinymce.widgets import TinyMCE
from captcha.fields import CaptchaField
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.user_groups.models import Group

class RequestForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = Request
        fields = "__all__"

class HelpFileAdminForm(TendenciBaseForm):
    answer = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':HelpFile._meta.app_label,
        'storme_model':HelpFile._meta.model_name.lower()}))

    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=False)

    status_detail = forms.ChoiceField(choices=(('draft',_('Draft')),('active',_('Active'))))

    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True, status_detail="active"), required=True, empty_label=None)

    class Meta:
        model = HelpFile
        fields = (
            'question',
            'slug',
            'answer',
            'group',
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
            'status_detail',
        )

    def __init__(self, *args, **kwargs):
        super(HelpFileAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['group'].initial = Group.objects.get_initial_group_id()

    def clean_syndicate(self):
        """
        clean method for syndicate added due to the update
        done on the field BooleanField -> NullBooleanField
        NOTE: BooleanField is converted to NullBooleanField because
        some Boolean data has value of None than False. This was updated
        on Django 1.6. BooleanField cannot have a value of None.
        """
        data = self.cleaned_data.get('syndicate', False)
        if data:
            return True
        else:
            return False


class HelpFileForm(TendenciBaseForm):
    answer = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':HelpFile._meta.app_label,
        'storme_model':HelpFile._meta.model_name.lower()}))

    status_detail = forms.ChoiceField(
        choices=(('draft',_('Draft')),('active',_('Active'))))

    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=False)

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
            'status_detail',
        )

        fieldsets = [(_('Help File Information'), {
                      'fields': ['question',
                                 'slug',
                                 'answer',
                                 'level',
                                 'topics',
                                 ],
                      'legend': ''
                      }),
                      (_('Flags'), {
                      'fields': ['is_faq',
                                 'is_featured',
                                 'is_video',
                                 ],
                        'classes': ['flags'],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['syndicate',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(HelpFileForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['answer'].widget.mce_attrs['app_instance_id'] = 0

        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields: self.fields.pop('status_detail')
            if 'allow_anonymous_view' in self.fields: self.fields.pop('allow_anonymous_view')
            if 'user_perms' in self.fields: self.fields.pop('user_perms')
            if 'member_perms' in self.fields: self.fields.pop('member_perms')
            if 'group_perms' in self.fields: self.fields.pop('group_perms')
            if 'syndicate' in self.fields: self.fields.pop('syndicate')

    def clean_syndicate(self):
        """
        clean method for syndicate added due to the update
        done on the field BooleanField -> NullBooleanField
        NOTE: BooleanField is converted to NullBooleanField because
        some Boolean data has value of None than False. This was updated
        on Django 1.6. BooleanField cannot have a value of None.
        """
        data = self.cleaned_data.get('syndicate', False)
        if data:
            return True
        else:
            return False