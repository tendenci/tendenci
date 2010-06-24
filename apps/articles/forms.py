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

    body = forms.CharField(required=False, max_length=10000, 
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Article._meta.app_label, 
        'storme_model':Article._meta.module_name.lower()}))


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
      
#    def __init__(self, user=None, *args, **kwargs):
#        self.user = user 
#        super(ArticleEditForm, self).__init__(*args, **kwargs)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(ArticleEditForm, self).__init__(*args, **kwargs)

        if self.instance.id: self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.id
        else: self.fields['body'].widget.mce_attrs['app_instance_id'] = "0"