from news.models import News
from perms.forms import TendenciBaseForm

class NewsForm(TendenciBaseForm):
    class Meta:
        model = News
        fields = (
        'headline',
        'slug',
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
        'tags',
        'allow_anonymous_view',
        'allow_user_view',
        'allow_user_edit',
        'syndicate',
        'status',
        'status_detail',
        'user_perms',
        )
      
    def __init__(self, user=None, *args, **kwargs): 
        self.user = user
        super(NewsForm, self).__init__(user, *args, **kwargs)
        
        
        
        