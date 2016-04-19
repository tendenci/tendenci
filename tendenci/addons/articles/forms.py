from datetime import datetime, date

from django import forms
from django.forms.util import ErrorList
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from tendenci.addons.articles.models import Article
from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.core.base.fields import SplitDateTimeField
from tendenci.core.base.fields import EmailVerificationField
from tendenci.core.perms.utils import get_query_filters
from tendenci.core.site_settings.utils import get_setting
from tendenci.apps.user_groups.models import Group


SEARCH_CATEGORIES_ADMIN = (
    ('headline__icontains', _('Headline')),
    ('first_name__icontains', _('Author First Name')),
    ('last_name__icontains', _('Author Last Name')),
    ('id', _('Article ID')),
    ('owner__id', _('Article Parent ID(#)')),

    ('body__icontains', _('Body')),
    ('tags__icontains', _('Tags')),

    ('creator__id', _('Creator Userid(#)')),
    ('creator__username', _('Creator Username')),

    ('featured', _('Featured Article')),

    ('owner__id', _('Owner Userid(#)')),
    ('owner__username', _('Owner Username')),

    ('status_detail__icontains', _('Status Detail')),
    ('syndicate', _('Syndicate')),
)

SEARCH_CATEGORIES = (
    ('headline__icontains', _('Headline')),
    ('last_name__icontains', _('Author Last Name')),
    ('first_name__icontains', _('Author First Name')),
    ('id', _('Article ID')),

    ('body__icontains', _('Body')),
    ('tags__icontains', _('Tags')),
)

CONTRIBUTOR_CHOICES = (
    (Article.CONTRIBUTOR_AUTHOR, mark_safe(_('Author <i class="gauthor-info fa fa-lg fa-question-circle"></i>'))),
    (Article.CONTRIBUTOR_PUBLISHER, mark_safe(_('Publisher <i class="gpub-info fa fa-lg fa-question-circle"></i>')))
)
GOOGLE_PLUS_HELP_TEXT = _('Additional Options for Authorship <i class="gauthor-help fa fa-lg fa-question-circle"></i><br>Additional Options for Publisher <i class="gpub-help fa fa-lg fa-question-circle"></i>')


class ArticleSearchForm(forms.Form):
    search_category = forms.ChoiceField(choices=SEARCH_CATEGORIES_ADMIN, required=False)
    q = forms.CharField(required=False)
    filter_date = forms.BooleanField(required=False)
    date = forms.DateField(initial=date.today(), required=False)

    def __init__(self, *args, **kwargs):
        is_superuser = kwargs.pop('is_superuser', None)
        super(ArticleSearchForm, self).__init__(*args, **kwargs)

        if not is_superuser:
            self.fields['search_category'].choices = SEARCH_CATEGORIES

    def clean(self):
        cleaned_data = self.cleaned_data
        q = self.cleaned_data.get('q', None)
        cat = self.cleaned_data.get('search_category', None)
        filter_date = self.cleaned_data.get('filter_date', None)
        date = self.cleaned_data.get('date', None)

        if cat is None or cat == "" :
            if not (q is None or q == ""):
                self._errors['search_category'] =  ErrorList([_('Select a category')])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                x = int(q)
            except ValueError:
                self._errors['q'] = ErrorList([_('Must be an integer')])

        if filter_date:
            if date is None or date == "":
                self._errors['date'] = ErrorList([_('Please select a date')])

        return cleaned_data


class ArticleForm(TendenciBaseForm):
    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%'},
        mce_attrs={'storme_app_label': Article._meta.app_label,
        'storme_model': Article._meta.module_name.lower()}))

    release_dt = SplitDateTimeField(label=_('Release Date/Time'),
        initial=datetime.now())

    contributor_type = forms.ChoiceField(choices=CONTRIBUTOR_CHOICES,
                                         initial=Article.CONTRIBUTOR_AUTHOR,
                                         widget=forms.RadioSelect())

    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')), ('inactive', _('Inactive')), ('pending', _('Pending')),))
    email = EmailVerificationField(label=_("Email"), required=False)
    group = forms.ChoiceField(required=True, choices=[])

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
            'contributor_type',
            'first_name',
            'last_name',
            'google_profile',
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

        fieldsets = [(_('Article Information'), {
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
                      (_('Contributor'), {
                       'fields': ['contributor_type',
                                  'google_profile'],
                       'classes': ['boxy-grey'],
                      }),
                      (_('Author'), {
                      'fields': ['first_name',
                                 'last_name',
                                 'phone',
                                 'fax',
                                 'email',
                                 ],
                        'classes': ['contact'],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
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

        default_groups = Group.objects.filter(status=True, status_detail="active")

        if self.user and not self.user.profile.is_superuser:
            if 'status_detail' in self.fields:
                self.fields.pop('status_detail')

            filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
            groups = default_groups.filter(filters).distinct()
            groups_list = list(groups.values_list('pk', 'name'))

            users_groups = self.user.profile.get_groups()
            for g in users_groups:
                if [g.id, g.name] not in groups_list:
                    groups_list.append([g.id, g.name])
        else:
            groups_list = default_groups.values_list('pk', 'name')

        self.fields['group'].choices = groups_list
        self.fields['google_profile'].help_text = mark_safe(GOOGLE_PLUS_HELP_TEXT)
        self.fields['timezone'].initial = settings.TIME_ZONE

    def clean_group(self):
        group_id = self.cleaned_data['group']

        try:
            group = Group.objects.get(pk=group_id)
            return group
        except Group.DoesNotExist:
            raise forms.ValidationError(_('Invalid group selected.'))

