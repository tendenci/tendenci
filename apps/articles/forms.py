from django import forms
from django.contrib.auth.models import User
from articles.models import Article

class ArticleForm(forms.ModelForm):
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
        'enclosure_url',
        'enclosure_type',
        'enclosure_length',
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
        super(ArticleForm, self).__init__(*args, **kwargs)

class ArticleEditForm(forms.ModelForm):
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
        'enclosure_url',
        'enclosure_type',
        'enclosure_length',
        'allow_anonymous_view',
        'allow_anonymous_edit',
        'allow_user_view',
        'allow_user_edit',
        'syndicate',
        'featured',
        'not_official_content',
        'owner',
        'status',
        'status_detail',
        )
      
    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(ArticleEditForm, self).__init__(*args, **kwargs)