from django import forms
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE

from before_and_after.models import BeforeAndAfter, Category, Subcategory

class BnAForm(TendenciBaseForm):
    class Meta:
        model = BeforeAndAfter
        
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':BeforeAndAfter._meta.app_label,
        'storme_model':BeforeAndAfter._meta.module_name.lower()}))
        
    status_detail = forms.ChoiceField(choices=(('active','Active'),('inactive','Inactive')))
    
    def __init__(self, *args, **kwargs):
        super(BnAForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
            
    def save(self, *args, **kwargs):
        bna = super(BnAForm, self).save(commit=False)
        print bna.id
        print self.current_user
        if not bna.id:
            bna.creator = self.current_user
            bna.creator_username = self.current_user.username
            
        bna.owner = self.current_user
        bna.owner_username = self.current_user.username
        bna.save()
        return bna

class SearchForm(forms.Form):
    category = forms.ModelChoiceField(
                        queryset=Category.objects.all(),
                        required=False,
                    )
    subcategory = forms.ModelChoiceField(
                        queryset=Subcategory.objects.all(),
                        required=False,
                    )
    q = forms.CharField(required=False)
