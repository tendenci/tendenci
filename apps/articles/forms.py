from django.forms import ModelForm
from articles.models import Article

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        exclude = ('guid',)
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
        'allow_site_user_view',
        'allow_member_view',
        'allow_site_user_edit',
        'allow_member_edit',

        'syndicate',
        'featured',
        'not_official_content',
        'owner',
        'status',
        'status_detail',
        )
