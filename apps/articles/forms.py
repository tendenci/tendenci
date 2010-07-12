from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from articles.models import Article
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

STATUS_CHOICES = (('active','Active'),('inactive','Inactive'), ('pending','Pending'),)

class ArticleForm(TendenciBaseForm):

    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Article._meta.app_label, 
        'storme_model':Article._meta.module_name.lower()}))
    
    release_dt = SplitDateTimeField(label=_('Release Date/Time'),
        initial=datetime.now())

#    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)

#    def clean_status_detail(self):
#        data = self.cleaned_data['status_detail']
#        print 'data:', dir(data)
#        return data

#    def clean(self):
#        cleaned_data = self.cleaned_data
#        print 'self', self.errors
#        return cleaned_data

    class Meta:
        model = Article
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
        'featured',
        'not_official_content',
        'status',
        'status_detail',
        )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user 
        super(ArticleForm, self).__init__(user, *args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0