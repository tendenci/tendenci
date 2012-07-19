from django import forms
from django.utils.translation import ugettext_lazy as _
from user_groups.models import Group
from imports.utils import get_header_list_from_content

KEY_CHOICES = (('email','Email'),
               ('first_name,last_name,email','First Name and Last Name and Email'),
               ('first_name,last_name,phone','First Name and Last Name and Phone'),
               ('first_name,last_name,company','First Name and Last Name and Company'),
               ('username','Username'),)

class UserImportForm(forms.Form):
    file  = forms.FileField(widget=forms.FileInput(attrs={'size': 35}))
    interactive = forms.CharField(widget=forms.RadioSelect(choices=((1,'Interactive'),
                                                          (0,'Not Interactive (no login)'),)), initial=0,)
    override = forms.CharField(widget=forms.RadioSelect(choices=((0,'Blank Fields'),
                                                          (1,'All Fields (override)'),)), initial=0, )
    key = forms.ChoiceField(initial="email", choices=KEY_CHOICES)
    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=1, 
                                                                 status_detail='active').order_by('name'),
                                                                 empty_label='Select One', required=False)
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