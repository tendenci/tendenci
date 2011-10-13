from django import forms
from django.utils.translation import ugettext_lazy as _

from perms.forms import TendenciBaseForm
from perms.utils import is_admin
from pages.models import Page
from navs.models import Nav, NavItem

class NavForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    
    class Meta:
        model = Nav
        fields = (
            'title',
            'description',
            'megamenu',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status',
            'status_detail',
            )

        fieldsets = [('Nav Information', {
                      'fields': ['title',
                                 'description',
                                 'megamenu',
                                 ],
                      'legend': ''
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
                      'fields': ['status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })
                    ]

class PageSelectForm(forms.Form):
    pages = forms.ModelMultipleChoiceField(label = _('Pages'),
                queryset = Page.objects.all(), widget=forms.CheckboxSelectMultiple)
    
    def __init__(self, *args, **kwargs):
        super(PageSelectForm, self).__init__(*args, **kwargs)

class ItemForm(forms.ModelForm):
    
    class Meta:
        model = NavItem
        fields = (
            'label',
            'title',
            'css',
            'ordering',
            'level',
            'page',
            'url',
            )
    
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        #we dont need the select widget for this since it will be hidden
        self.fields['page'].required = False
        self.fields['page'].widget = forms.TextInput()
        self.fields['ordering'].widget = forms.HiddenInput()
        self.fields['level'].widget = forms.HiddenInput()
