from django import forms
from django.utils.translation import ugettext_lazy as _
from tendenci.apps.user_groups.models import Group
from tendenci.apps.imports.utils import get_header_list_from_content
from tendenci.apps.imports.models import Import

KEY_CHOICES = (('email',_('Email')),
               ('first_name,last_name,email',_('First Name and Last Name and Email')),
               ('first_name,last_name,phone',_('First Name and Last Name and Phone')),
               ('first_name,last_name,company',_('First Name and Last Name and Company')),
               ('username',_('Username')),)


class UserImportForm(forms.Form):
    file  = forms.FileField(widget=forms.FileInput(attrs={'size': 35}))
    interactive = forms.CharField(widget=forms.RadioSelect(choices=((True,_('Interactive')),
                                                          (False,_('Not Interactive (no login)')),)), initial=False,)
    override = forms.CharField(widget=forms.RadioSelect(choices=((False,_('Blank Fields')),
                                                          (True,_('All Fields (override)')),)), initial=False, )
    key = forms.ChoiceField(initial="email", choices=KEY_CHOICES)
    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True,
                                                                 status_detail='active').order_by('name'),
                                                                 empty_label=_('Select One'), required=False)
    clear_group_membership = forms.BooleanField(initial=0, required=False)

    def clean(self):
        # test if the file is missing any key
        if self.cleaned_data.has_key('key') and self.cleaned_data.has_key('file'):
            key_list = self.cleaned_data["key"].split(',')
            file = self.cleaned_data['file']
            file_content = file.read()
            fields = get_header_list_from_content(file_content, file.name)

            fields = [f.strip('"') for f in fields]

            missing_keys = []
            for key in key_list:
                if key not in fields:
                    missing_keys.append(key)

            if missing_keys:
                missing_keys = ','.join(missing_keys)
                raise forms.ValidationError(_("The uploaded file lacks the required field(s) as the identity for duplicates: %s." % missing_keys))
        return self.cleaned_data


class UserImportPreviewForm(forms.Form):
    interactive = forms.CharField(widget=forms.HiddenInput(), required=False)
    override = forms.CharField(widget=forms.HiddenInput(), required=False)
    key = forms.CharField(widget=forms.HiddenInput())
    group = forms.CharField(widget=forms.HiddenInput(), required=False)
    clear_group_membership = forms.CharField(widget=forms.HiddenInput(), required=False)


class ImportForm(forms.ModelForm):
    class Meta:
        model = Import
        fields = ('file',)
