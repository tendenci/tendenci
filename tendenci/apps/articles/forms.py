from datetime import datetime, date

from django import forms
from django.conf import settings
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.articles.models import Article
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.base.fields import EmailVerificationField
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.categories.forms import CategoryField
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.user_groups.models import Group
from tendenci.apps.files.validators import FileValidator
from tendenci.apps.files.models import File


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

def get_search_group_choices():
    article_group_ids = set(Article.objects.all().values_list('group', flat=True))
    groups = Group.objects.filter(
                    id__in=article_group_ids).distinct(
                    ).order_by('name').values_list('id', 'label', 'name')
    return [(id, label or name) for id, label, name in groups]

class ArticleSearchForm(FormControlWidgetMixin, forms.Form):
    search_category = forms.ChoiceField(
        choices=SEARCH_CATEGORIES_ADMIN,
        required=False,
        label=_(u'Search by')
    )
    q = forms.CharField(required=False)
    category = CategoryField(label=_('All Categories'), choices=[], required=False)
    sub_category = CategoryField(label=_('All Subcategories'), choices=[], required=False)
    filter_date = forms.BooleanField(required=False)
    date = forms.DateField(initial=date.today(), required=False)
    group = forms.ChoiceField(label=_('Group'), required=False, choices=[])

    def __init__(self, *args, **kwargs):
        is_superuser = kwargs.pop('is_superuser', None)
        super(ArticleSearchForm, self).__init__(*args, **kwargs)
        
        # group
        group_choices = get_search_group_choices()
        self.fields['group'].choices = [('','All Groups')] + list(group_choices)

        if not is_superuser:
            self.fields['search_category'].choices = SEARCH_CATEGORIES

        categories, sub_categories = Article.objects.get_categories()

        categories = [(cat.name, cat) for cat in categories]
        categories.insert(0, ('', _('All Categories (%d)' % len(categories))))
        sub_categories = [(cat.name, cat) for cat in sub_categories]
        sub_categories.insert(0, ('', _('All Subcategories (%d)' % len(sub_categories))))

        self.fields['category'].choices = categories
        self.fields['sub_category'].choices = sub_categories

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
                int(q)
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
        'storme_model': Article._meta.model_name.lower()}))

    release_dt = forms.SplitDateTimeField(label=_('Release Date/Time'),
                          input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
                          input_time_formats=['%I:%M %p', '%H:%M:%S'])

    contributor_type = forms.ChoiceField(choices=CONTRIBUTOR_CHOICES,
                                         initial=Article.CONTRIBUTOR_AUTHOR,
                                         widget=forms.RadioSelect())
    thumbnail_file = forms.FileField(
            label=_('Thumbnail'),
            validators=[FileValidator(allowed_extensions=('.jpg', '.jpeg', '.gif', '.png'))],
            required=False,
            help_text=_('Only jpg, gif, or png images.'))        
    syndicate = forms.BooleanField(label=_('Include in RSS feed'), required=False, initial=True)
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
            'thumbnail_file',
            'source',
            'website',
            'release_dt',
            'timezone',
            'contributor_type',
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

        fieldsets = [(_('Article Information'), {
                      'fields': ['headline',
                                 'slug',
                                 'summary',
                                 'body',
                                 'thumbnail_file',
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
                       'fields': ['contributor_type',],
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
        
        if self.instance.thumbnail:
            self.initial['thumbnail_file'] = self.instance.thumbnail.file

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
        self.fields['timezone'].initial = settings.TIME_ZONE

        self.fields['release_dt'].initial = datetime.now()

    def save(self, *args, **kwargs):
        article = super(ArticleForm, self).save(*args, **kwargs)

        content_type = ContentType.objects.get_for_model(Article)
        thumbnail_file = self.cleaned_data['thumbnail_file']

        if thumbnail_file:
            file_object, created = File.objects.get_or_create(
                file=thumbnail_file,
                defaults={
                    'name': thumbnail_file.name,
                    'content_type': content_type,
                    'object_id': article.pk,
                    'is_public': article.allow_anonymous_view,
                    'tags': article.tags,
                    'creator': self.user,
                    'owner': self.user,
                })

            article.thumbnail = file_object
            article.save(log=False)
        else:
            # clear thumbnail if box checked
            if article.thumbnail:
                article.thumbnail = None
                article.save(log=False)
                File.objects.filter(
                    content_type=content_type,
                    object_id=article.pk).delete()

        return article

    def clean_group(self):
        group_id = self.cleaned_data['group']

        try:
            group = Group.objects.get(pk=group_id)
            return group
        except Group.DoesNotExist:
            raise forms.ValidationError(_('Invalid group selected.'))

    def clean_syndicate(self):
        """
        clean method for syndicate added due to the update
        done on the field BooleanField -> NullBooleanField
        NOTE: BooleanField is converted to NullBooleanField because
        some Boolean data has value of None than False. This was updated
        on Django 1.6. BooleanField cannot have a value of None.
        """
        data = self.cleaned_data.get('syndicate', False)
        if data:
            return True
        else:
            return False
