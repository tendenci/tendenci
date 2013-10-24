from django import forms
from django.utils.translation import ugettext_lazy as _

from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.apps.pages.models import Page
from tendenci.apps.navs.models import Nav, NavItem

class NavForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    
    class Meta:
        model = Nav
        fields = (
            'title',
            'description',
            # 'megamenu', # needs CSS first
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status_detail',
            )

        fieldsets = [('Nav Information', {
                      'fields': ['title',
                                 'description',
                                 # 'megamenu', # needs CSS first
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
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })
                    ]

class PageSelectForm(forms.Form):
    pages = forms.ModelMultipleChoiceField(label = _('Pages'),
                queryset = Page.objects.exclude(status_detail='archive').order_by('title'), widget=forms.CheckboxSelectMultiple)
    
    def __init__(self, *args, **kwargs):
        super(PageSelectForm, self).__init__(*args, **kwargs)

class ItemForm(forms.ModelForm):
    
    class Meta:
        model = NavItem
        fields = (
            'label',
            'title',
            'css',
            'position',
            'level',
            'page',
            'url',
            'new_window',
            )
    
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        #we dont need the select widget for this since it will be hidden
        self.fields['page'].required = False
        self.fields['page'].widget = forms.TextInput()
        self.fields['position'].widget = forms.HiddenInput()
        self.fields['level'].widget = forms.HiddenInput()

    def clean_url(self):
        ''' Fix URLs that don't start with / or http '''

        if self.cleaned_data['url']:
            if not self.cleaned_data['url'][:4].lower() == "http" and not self.cleaned_data['url'][:1] == "/":
                # Append a beginning forward slash if none and not http
                self.cleaned_data['url'] = "/%s" % self.cleaned_data['url']

        return self.cleaned_data['url']

#     def clean_page(self):
#     ''' Create pages that don't exist yet '''
#
#         if not self.cleaned_data['page']:
#             newpage = Page(title=self.cleaned_data['label'],slug=self.cleaned_data.get('url')),creator_id=
#             newpage.save()
#         
#         return self.cleaned_data['page']
