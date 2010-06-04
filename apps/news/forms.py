from django import forms

from news.models import News
from perms.forms import AuditingBaseForm

class NewsForm(AuditingBaseForm):
    class Meta:
        model = News
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
        'enclosure_url',
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
        
        
        
        