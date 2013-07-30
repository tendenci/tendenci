from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from tendenci.addons.articles.models import Article
from tendenci.core.perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from tendenci.core.base.fields import SplitDateTimeField
from tendenci.core.base.fields import EmailVerificationField
from tendenci.apps.user_groups.models import Group


class ArticleForm(TendenciBaseForm):
    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': Article._meta.app_label,
        'storme_model': Article._meta.module_name.lower()}))

    release_dt = SplitDateTimeField(label=_('Release Date/Time'),
        initial=datetime.now())

    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending'),))
    email = EmailVerificationField(label=_("Email"), required=False)
    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True, status_detail="active"), required=True, empty_label=None)

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
            'group',
            'tags',
            'allow_anonymous_view',
            'syndicate',
            'user_perms',
            'member_perms',
            'group_perms',
            'status_detail',
        )

        fieldsets = [('Article Information', {
                      'fields': ['headline',
                                 'slug',
                                 'summary',
                                 'body',
                                 'group',
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
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['group'].initial = Group.objects.get_initial_group_id()

        if self.user and not self.user.profile.is_superuser:
            if 'status_detail' in self.fields:
                self.fields.pop('status_detail')
