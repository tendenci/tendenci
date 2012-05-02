from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from articles.models import Article
from perms.utils import is_admin, is_developer
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class ArticleForm(TendenciBaseForm):
    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Article._meta.app_label, 
        'storme_model':Article._meta.module_name.lower()}))

    release_dt = SplitDateTimeField(label=_('Release Date/Time'),
        initial=datetime.now())

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

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
            'syndicate',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
            'status_detail',
        )

        fieldsets = [('Article Information', {
                      'fields': ['headline',
                                 'slug',
                                 'summary',
                                 'body',
                                 'tags',
                                 'source', 
                                 'website',
                                 'release_dt',
                                 'timezone',
                                 ],
                      'legend': ''
                      }),
                      ('Contact', {
                      'fields': ['first_name',
                                 'last_name',
                                 'phone',
                                 'fax',
                                 'email',
                                 ],
                        'classes': ['contact'],
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['syndicate',
                                 'status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0

        if not is_admin(self.user):
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        if not is_developer(self.user):
            if 'status' in self.fields: self.fields.pop('status')
