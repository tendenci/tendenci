from django import forms
from user_groups.models import Group

KEY_CHOICES = (('email','email'),
               ('first_name,last_name,email','first_name and last_name and email'),
               ('first_name,last_name,phone','first_name and last_name and phone'),
               ('first_name,last_name,company','first_name and last_name and company'),
               ('username','username'),)

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
    
class UserImportPreviewForm(forms.Form):
    interactive = forms.CharField(widget=forms.HiddenInput(), required=False)
    override = forms.CharField(widget=forms.HiddenInput(), required=False)
    key = forms.CharField(widget=forms.HiddenInput())
    group = forms.CharField(widget=forms.HiddenInput(), required=False)
    clear_group_membership = forms.CharField(widget=forms.HiddenInput(), required=False)
    
