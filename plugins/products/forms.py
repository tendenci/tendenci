from django import forms

from products.models import Product, Category, Subcategory
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class ProductForm(TendenciBaseForm):
    class Meta:
        model = Product
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    description = forms.CharField(required=True,widget=TinyMCE(attrs={'style':'width:100%'},mce_attrs={'storme_app_label':u'products','storme_model':Product._meta.module_name.lower()}))

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