from datetime import datetime, date

from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from tendenci.addons.articles.models import Article
from tendenci.core.perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from tendenci.core.base.fields import SplitDateTimeField
from tendenci.core.base.fields import EmailVerificationField
from tendenci.core.perms.utils import get_query_filters
from tendenci.apps.user_groups.models import Group


SEARCH_CATEGORIES_ADMIN = (
    ('headline__icontains', 'Headline'),
    ('first_name__icontains', 'Author First Name'),
    ('last_name__icontains', 'Author Last Name'),
    ('id', 'Article ID'),
    ('owner__id', 'Article Parent ID(#)'),

    ('body__icontains', 'Body'),
    ('tags__icontains', 'Tags'),

    ('creator__id', 'Creator Userid(#)'),
    ('creator__username', 'Creator Username'),

    ('featured', 'Featured Article'),

    ('owner__id', 'Owner Userid(#)'),
    ('owner__username', 'Owner Username'),

    ('status_detail__icontains', 'Status Detail'),
    ('syndicate', 'Syndicate'),
)

SEARCH_CATEGORIES = (
    ('headline__icontains', 'Headline'),
    ('last_name__icontains', 'Author Last Name'),
    ('first_name__icontains', 'Author First Name'),
    ('id', 'Article ID'),

    ('body__icontains', 'Body'),
    ('tags__icontains', 'Tags'),
)

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
                self._errors['search_category'] =  ErrorList(['Select a category'])

        if cat in ('id', 'owner__id', 'creator__id') :
            try:
                x = int(q)
            except ValueError:
                self._errors['q'] = ErrorList(['Must be an integer'])

        if filter_date:
            if date is None or date == "":
                self._errors['date'] = ErrorList(['Please select a date'])

        return cleaned_data


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

    def clean_group(self):
        group_id = self.cleaned_data['group']

        try:
            group = Group.objects.get(pk=group_id)
            return group
        except Group.DoesNotExist:
            raise forms.ValidationError(_('Invalid group selected.'))

