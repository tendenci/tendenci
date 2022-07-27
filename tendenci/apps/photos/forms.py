from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms.models import BaseModelFormSet

from tendenci.apps.user_groups.models import Group
from tendenci.apps.photos.models import Image, PhotoSet, License, PhotoCategory
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.perms.utils import get_query_filters, get_groups_query_filters
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.forms import FormControlWidgetMixin


class PhotoBaseFormSet(BaseModelFormSet):
    def __init__(self,  *args, **kwargs): 
        self.photo_set = kwargs.pop("photo_set", None)
        super(PhotoBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        if hasattr(self, 'photo_set'):
            kwargs['photo_set'] = self.photo_set
        return super(PhotoBaseFormSet, self)._construct_form(i, **kwargs)


class PhotoForm(forms.ModelForm):

    class Meta:
        model = Image
        exclude=(
            'title_slug',
            'creator_username',
            'owner_username',
            'photoset',
            'is_public',
            'owner',
            'safetylevel',
            'exif_data',
            'allow_anonymous_view',
            'status',
            'status_detail',
        ),

    def __init__(self, photo_set, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        if photo_set.cat:
            self.fields['cat'].queryset = PhotoCategory.objects.filter(parent_id=photo_set.cat.id)
        else:
            self.fields['cat'].queryset = PhotoCategory.objects.none()


class PhotoSetSearchForm(FormControlWidgetMixin, forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    cat = forms.ModelChoiceField(label=_("Category"),
                                      queryset=PhotoCategory.objects.filter(parent=None),
                                      empty_label="-----------",
                                      required=False)

    def __init__(self, *args, **kwargs):
        super(PhotoSetSearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs.update({'placeholder': _('Enter name / keywords')})

        # setup categories
        cats = PhotoCategory.objects.filter(parent__isnull=True)
        cats_count = cats.count()
        if cats_count:
            self.fields['cat'].queryset = cats
            self.fields['cat'].empty_label = _('Categories (%(c)s)' % {'c' : cats_count})
            data = args[0]
            if data:
                try:
                    cat = int(data.get('cat', 0))
                except ValueError:
                    cat = 0
        else:
            del self.fields['cat']


class LicenseField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.id == 1:
            return obj.name
        return mark_safe("%s -- <a href='%s'>see details</a>" % (obj.name, obj.deed))

class PhotoAdminForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))
    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True, status_detail="active"), required=True, empty_label=None)

    class Meta:
        model = Image
        fields = (
            'image',
            #'title',
            'caption',
            'tags',
            'allow_anonymous_view',
            #'syndicate',
            'group',
            'status_detail',
            'license',
        )
        fieldsets = [(_('Photo Set Information'), {
            'fields': ['description',
                       'tags',
                       'group',
                       ],
            'legend': ''
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
                'fields': ['status_detail'],
                'classes': ['admin-only'],
                })]

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


class PhotoBatchEditForm(TendenciBaseForm):
    class Meta:
        model = Image
        exclude = (
            'title_slug',
            'creator_username',
            'owner_username',
            'photoset',
            'is_public',
            'owner',
            'safetylevel',
            'exif_data',
            'allow_anonymous_view',
            'status_detail',
            'status',
        )

    def __init__(self, *args, **kwargs):
        super(PhotoBatchEditForm, self).__init__(*args, **kwargs)
        if 'group' in self.fields:
            self.fields['group'].initial = Group.objects.get_initial_group_id()


class PhotoEditForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')),
                ('pending',_('Pending')),))
    license = LicenseField(queryset=License.objects.all(),
                widget = forms.RadioSelect(), empty_label=None)

    class Meta:
        model = Image

        fields = (
            'title',
            'caption',
            'photographer',
            'license',
            'tags',
            'group',
            'cat',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'status_detail'
        )

        fieldsets = [
                (_('Photo Information'), {
                      'fields': [
                          'title',
                          'caption',
                          'photographer',
                          'tags',
                          'group',
                          'cat',
                          'license',
                      ], 'legend': '',
                  }),
                (_('Permissions'), {
                      'fields': [
                          'allow_anonymous_view',
                          'user_perms',
                          'member_perms',
                          'group_perms',
                      ], 'classes': ['permissions'],
                  }),

                (_('Administrator Only'), {
                      'fields': [
                          'syndicate',
                          'status_detail',
                      ], 'classes': ['admin-only'],
                  }),
        ]

    safetylevel = forms.HiddenInput()

    def __init__(self, *args, **kwargs):
        super(PhotoEditForm, self).__init__(*args, **kwargs)
        default_groups = Group.objects.filter(status=True, status_detail="active")

        if self.user and not self.user.profile.is_superuser:
            if get_setting('module', 'user_groups', 'permrequiredingd') == 'change':
                filters = get_groups_query_filters(self.user,)
            else:
                filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
            default_groups = default_groups.filter(filters).distinct()

        self.fields['group'].queryset = default_groups
        self.fields['group'].empty_label = None

        # photo cat
        [photo_set] = self.instance.photoset.all()[:1] or [None]
        if photo_set and photo_set.cat:
            self.fields['cat'].queryset = PhotoCategory.objects.filter(parent_id=photo_set.cat.id)
            self.fields['cat'].required = False
        else:
            del self.fields['cat']


class PhotoSetForm(TendenciBaseForm):
    """ Photo-Set Add/Edit-Form """

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

    class Meta:
        model = PhotoSet
        fields = (
            'name',
            'description',
            'group',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'cat',
            'status_detail',
        )

        fieldsets = [(_('Photo Set Information'), {
                      'fields': ['name',
                                 'description',
                                 'group',
                                 'tags',
                                 ],
                      'legend': ''
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                      (_('Category'), {
                        'fields': ['cat',
                                   ],
                        'classes': ['boxy-grey'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(PhotoSetForm, self).__init__(*args, **kwargs)
        default_groups = Group.objects.filter(status=True, status_detail="active")

        if self.user and not self.user.profile.is_superuser:
            if 'status_detail' in self.fields:
                self.fields.pop('status_detail')

            if get_setting('module', 'user_groups', 'permrequiredingd') == 'change':
                filters = get_groups_query_filters(self.user,)
            else:
                filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
            default_groups = default_groups.filter(filters).distinct()

        self.fields['group'].queryset = default_groups
        self.fields['group'].empty_label = None

        # cat and sub_cat
        self.fields['cat'].required = False
        self.fields['cat'].queryset = PhotoCategory.objects.filter(parent__isnull=True)

        if args:
            post_data = args[0]
        else:
            post_data = None
        if post_data:
            try:
                cat = int(post_data.get('cat', '0'))
            except ValueError:
                cat = None

        if self.user and self.user.profile.is_superuser:
            self.fields['cat'].help_text = mark_safe('<a href="{0}">{1}</a>'.format(
                        reverse('admin:photos_photocategory_changelist'),
                            _('Manage Categories'),))

