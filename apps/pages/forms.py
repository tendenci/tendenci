from django import forms

from pages.models import Page
from perms.forms import AuditingBaseForm

class PageForm(AuditingBaseForm):
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
        super(PageForm, self).__init__(user, *args, **kwargs)