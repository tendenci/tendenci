from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from news.models import News
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class NewsForm(TendenciBaseForm):
    STATUS_CHOICES = (('active','Active'),('inactive','Inactive'), ('pending','Pending'),)

    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':News._meta.app_label, 
        'storme_model':News._meta.module_name.lower()}))

    release_dt = SplitDateTimeField(label=_('Release Date/Time'), 
        initial=datetime.now())

    status_detail = forms.ChoiceField(choices=STATUS_CHOICES)
           
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
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0        
        
        
        