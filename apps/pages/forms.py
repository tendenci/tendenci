from pages.models import Page
from perms.forms import TendenciBaseForm

class PageForm(TendenciBaseForm):
    class Meta:
        model = Page
        fields = (
        'title',
        'content',
        'tags',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_member_view',
        'allow_user_edit',
        'allow_member_edit',
        'syndicate',
        'status',
        'status_detail',
        )
      
    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(PageForm, self).__init__(user, *args, **kwargs)