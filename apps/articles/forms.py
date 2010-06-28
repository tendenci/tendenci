from articles.models import Article
from perms.forms import TendenciBaseForm
from django import forms
from tinymce.widgets import TinyMCE

class ArticleForm(TendenciBaseForm):
    class Meta:
        model = Article
        fields = (
        'headline',
        'summary',
        'body',
        'source',
        'website',
        'release_dt',
        'timezone',
        'first_name',
        'last_name',
        'phone',
        'fax',
        'email',
        'category',
        'tags',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_user_edit',
        'syndicate',
        'featured',
        'not_official_content',
        'status',
        'status_detail',
        )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(ArticleForm, self).__init__(user, *args, **kwargs)