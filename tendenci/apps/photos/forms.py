from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from tendenci.apps.user_groups.models import Group
from tendenci.apps.photos.models import Image, PhotoSet, License
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.perms.utils import get_query_filters, get_groups_query_filters
from tendenci.apps.site_settings.utils import get_setting

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


class PhotoSetAddForm(TendenciBaseForm):
    """ Photo-Set Add-Form """

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
                     (_('Administrator Only'), {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(PhotoSetAddForm, self).__init__(*args, **kwargs)
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

#        if self.user.profile.is_superuser:
#            self.fields['status_detail'] = forms.ChoiceField(
#                choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))


class PhotoSetEditForm(TendenciBaseForm):
    """ Photo-Set Edit-Form """

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
                     (_('Administrator Only'), {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(PhotoSetEditForm, self).__init__(*args, **kwargs)
        default_groups = Group.objects.filter(status=True, status_detail="active")

        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields:
                self.fields.pop('status_detail')

            if get_setting('module', 'user_groups', 'permrequiredingd') == 'change':
                filters = get_groups_query_filters(self.user,)
            else:
                filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
            default_groups = default_groups.filter(filters).distinct()

        self.fields['group'].queryset = default_groups
        self.fields['group'].empty_label = None

