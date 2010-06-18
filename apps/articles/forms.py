from articles.models import Article
from perms.forms import AuditingBaseForm

class ArticleForm(AuditingBaseForm):
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
        'allow_anonymous_edit',
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
        
        
        
        