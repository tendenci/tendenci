from django import forms
from pages.models import Page

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = (
        'title',
        'content',

        'page_title',
        'meta_keywords',
        'meta_description',

        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
        'allow_user_edit',
        'allow_member_edit',

        'syndicate',
        'displaypagetemplate',

        'status',
        'status_detail',
        )
    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(PageForm, self).__init__(*args, **kwargs)

class PageEditForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = (
        'title',
        'content',

        'page_title',
        'meta_keywords',
        'meta_description',

        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
        'allow_user_edit',
        'allow_member_edit',

        'syndicate',
        'displaypagetemplate',

        'owner',
        'status',
        'status_detail',
        )
      
    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(PageEditForm, self).__init__(*args, **kwargs)