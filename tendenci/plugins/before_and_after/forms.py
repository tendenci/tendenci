from django import forms
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE

from before_and_after.models import BeforeAndAfter, Category, Subcategory

class BnAForm(TendenciBaseForm):
    class Meta:
        model = BeforeAndAfter
        
    description = forms.CharField(
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':BeforeAndAfter._meta.app_label,
        'storme_model':BeforeAndAfter._meta.module_name.lower()}))
        
    status_detail = forms.ChoiceField(choices=(('active','Active'),('inactive','Inactive')))
    
    def clean(self):
        data = self.cleaned_data
        cat = data.get('category')
        sub = data.get('subcategory', None)
        if sub:
            if sub.category != cat:
                raise forms.ValidationError(
                    "%s is not a subcategory of %s" % (sub, cat))
        return data

class SearchForm(forms.Form):
    category = forms.ModelChoiceField(
                        empty_label="Category",
                        queryset=Category.objects.all(),
                        required=False,
                    )
    subcategory = forms.ModelChoiceField(
                        empty_label="Subcategory",
                        queryset=Subcategory.objects.none(),
                        required=False,
                    )
    q = forms.CharField(required=False)
