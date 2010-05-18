from django.forms import ModelForm
from pages.models import Page

class PageForm(ModelForm):
    class Meta:
        model = Page
        exclude = ('guid',)
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
