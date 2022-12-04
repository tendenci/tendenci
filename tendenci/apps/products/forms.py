from django import forms

from .models import Product, Category
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE


class ProductForm(TendenciBaseForm):
    class Meta:
        model = Product
        fields = (
            'name',
            'slug',
            'brand',
            'url',
            'item_number',
            'category',
            'summary',
            'description',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status',
            'status_detail',
        )
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': Product._meta.app_label,
        'storme_model': Product._meta.model_name.lower()}))
