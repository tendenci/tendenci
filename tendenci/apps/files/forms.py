import os
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from django.template.defaultfilters import filesizeformat

from tendenci.apps.categories.models import Category
from tendenci.apps.files.fields import MultiFileField
from tendenci.apps.files.models import File, FilesCategory
from tendenci.apps.files.utils import get_max_file_upload_size, get_allowed_upload_file_exts
from tendenci.apps.perms.fields import GroupPermissionField, UserPermissionField, MemberPermissionField
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.perms.utils import update_perms_and_save, get_query_filters, get_groups_query_filters
from tendenci.apps.user_groups.models import Group
from tendenci.libs.form_utils.forms import BetterForm
from tendenci.apps.files.validators import FileValidator
from tendenci.apps.site_settings.utils import get_setting


class FileForm(TendenciBaseForm):

    file_cat = forms.ModelChoiceField(label=_("Category"),
                                      queryset=FilesCategory.objects.filter(parent=None),
                                      empty_label="-----------",
                                      required=False)
    file_sub_cat = forms.ModelChoiceField(label=_("Sub-Category"),
                                          queryset=FilesCategory.objects.none(),
                                          empty_label=_("Please choose a category first"),
                                          required=False)
    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')), ('inactive', _('Inactive')), ('pending', _('Pending'))))

    class Meta:
        model = File

        fields = (
            'file',
            'name',
            'group',
            'tags',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'file_cat',
            'file_sub_cat',
            'status_detail'
        )

        fieldsets = [('', {
                      'fields': [
                        'file',
                        'name',
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
                        'fields': ['file_cat',
                                   'file_sub_cat'
                                   ],
                        'classes': ['boxy-grey'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        default_groups = Group.objects.filter(status=True, status_detail="active")

        if args:
            post_data = args[0]
        else:
            post_data = None

        if not self.user.profile.is_superuser:
            del self.fields['status_detail']

            if get_setting('module', 'user_groups', 'permrequiredingd') == 'change':
                filters = get_groups_query_filters(self.user,)
            else:
                filters = get_query_filters(self.user, 'user_groups.view_group', **{'perms_field': False})
            default_groups = default_groups.filter(filters).distinct()

        self.fields['group'].queryset = default_groups
        self.fields['group'].empty_label = None

        if self.instance and self.instance.pk:
            self.fields['file_sub_cat'].queryset = FilesCategory.objects.filter(
                                                        parent=self.instance.file_cat)

        if post_data:
            file_cat = post_data.get('file_cat', '0')
            if file_cat and file_cat != '0' and file_cat != u'':
                file_cat = FilesCategory.objects.get(pk=int(file_cat))
                self.fields['file_sub_cat'].queryset = FilesCategory.objects.filter(parent=file_cat)
        if 'file' in self.fields:
            self.fields['file'].validators = [FileValidator()]


class TinymceUploadForm(forms.ModelForm):
    app_label = forms.CharField(required=True, max_length=100, error_messages={'required': "App label is required."})
    model = forms.CharField(required=True, max_length=50, error_messages={'required': "Model name is required."})
    object_id = forms.IntegerField(required=False)
    upload_type = forms.CharField(required=False, max_length=10)

    class Meta:
        model = File
        fields = (
            'file',)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            self.user = None
        request_data = kwargs.pop('request_data')
        super(TinymceUploadForm, self).__init__(*args, **kwargs)

        if request_data.method.lower() == 'post':
            upload_type = request_data.POST.get('upload_type', 'other')
        else:
            upload_type = request_data.GET.get('upload_type', 'other')
        allowed_exts = get_allowed_upload_file_exts(upload_type)
        self.fields['file'].validators = [FileValidator(allowed_extensions=allowed_exts)]


class MostViewedForm(forms.Form):
    """
    Takes in the date range and files type you're
    searching for and returns back a result list.
    """

    TYPES = (
      ('all', _('All File Types')),
      ('pdf', _('PDF Documents')),
      ('slides', _('Slides')),
      ('spreadsheet', _('Spreadsheets')),
      ('text', _('Text Documents')),
      ('zip', _('Zip Files')),
    )

    start_dt = forms.DateField(label=_('Start'))
    end_dt = forms.DateField(label=_('End'))
    file_type = forms.ChoiceField(label=_('File Type'), choices=TYPES)

    def __init__(self, *args, **kwargs):
        super(MostViewedForm, self).__init__(*args, **kwargs)
        self.fields['file_type'].widget.attrs['class'] = 'btn'


class FileSearchForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    file_cat = forms.ModelChoiceField(label=_("Category"),
                                      queryset=FilesCategory.objects.filter(parent=None),
                                      empty_label="-----------",
                                      required=False)
    file_sub_cat = forms.ModelChoiceField(label=_("Sub-Category"),
                                          queryset=FilesCategory.objects.none(),
                                          empty_label=_("Please choose a category first"),
                                          required=False)
    group = forms.ChoiceField(label=_('Group'), choices=[], required=False)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            self.user = None

        data = args[0] if args else kwargs['data'] if 'data' in kwargs else None
        category = data['file_cat'] if data and 'file_cat' in data else None

        super(FileSearchForm, self).__init__(*args, **kwargs)

        user = self.user or AnonymousUser()
        filters = get_query_filters(user, 'user_groups.view_group', **{'perms_field': False})
        groups = Group.objects.filter(filters).distinct()
        groups_list = [[g.id, g.name] for g in groups]
        if user.is_authenticated:
            users_groups = self.user.profile.get_groups()
            for g in users_groups:
                if [g.id, g.name] not in groups_list:
                    groups_list.append([g.id, g.name])

        groups_list.insert(0, ['', '------------'])
        self.fields['group'].choices = tuple(groups_list)

        # Update categories and subcategories choices
        main_categories = FilesCategory.objects.filter(parent__isnull=True)
        self.fields['file_cat'].queryset = main_categories
        if category:
            sub_categories = FilesCategory.objects.filter(parent=category)
            self.fields['file_sub_cat'].empty_label = "-----------"
            self.fields['file_sub_cat'].queryset = sub_categories


class FileSearchMinForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)


class FilewithCategoryForm(TendenciBaseForm):

    group = forms.ChoiceField(required=True, choices=[])

    file_cat = forms.ModelChoiceField(label=_("Category"),
                                      queryset=FilesCategory.objects.filter(parent=None),
                                      empty_label="-----------",
                                      required=False)
    file_sub_cat = forms.ModelChoiceField(label=_("Sub-Category"),
                                          queryset=FilesCategory.objects.none(),
                                          empty_label=_("Please choose a category first"),
                                          required=False)

    class Meta:
        model = File

        fields = (
            'file',
            'name',
            'group',
            'tags',
            'file_cat',
            'file_sub_cat',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
        )

    def __init__(self, *args, **kwargs):
        super(FilewithCategoryForm, self).__init__(*args, **kwargs)
        default_groups = Group.objects.filter(status=True, status_detail="active")

        if args:
            post_data = args[0]
        else:
            post_data = None

        if self.user and not self.user.profile.is_superuser:
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

        if self.instance and self.instance.pk:
            self.fields['file_sub_cat'].queryset = FilesCategory.objects.filter(
                                                        parent=self.instance.file_cat)

        if post_data:
            file_cat = post_data.get('file_cat', '0')
            if file_cat and file_cat != '0' and file_cat != u'':
                file_cat = FilesCategory.objects.get(pk=int(file_cat))
                self.fields['file_sub_cat'].queryset = FilesCategory.objects.filter(parent=file_cat)

        if 'file' in self.fields:
            self.fields['file'].validators = [FileValidator()]

    def clean_group(self):
        group_id = self.cleaned_data['group']

        try:
            group = Group.objects.get(pk=group_id)
            return group
        except Group.DoesNotExist:
            raise forms.ValidationError(_('Invalid group selected.'))

    def save(self, *args, **kwargs):
        file = super(FilewithCategoryForm, self).save(*args, **kwargs)

        file.save()

        #setup categories
        category = Category.objects.get_for_object(file, 'category')
        sub_category = Category.objects.get_for_object(file, 'sub_category')

        ## update the category of the file
        category_removed = False
        category = file.file_cat.name if file.file_cat else u''

        if category:
            Category.objects.update(file, category, 'category')
        else:  # remove
            category_removed = True
            Category.objects.remove(file, 'category')
            Category.objects.remove(file, 'sub_category')

        if not category_removed:
            # update the sub category of the article
            sub_category = file.file_sub_cat.name if file.file_sub_cat else u''
            if sub_category:
                Category.objects.update(file, sub_category, 'sub_category')
            else:  # remove
                Category.objects.remove(file, 'sub_category')

        #Save relationships
        file.save()

        return file


class MultiFileForm(BetterForm):
    files = MultiFileField(min_num=1, validators=[FileValidator()])
    group = forms.ChoiceField(required=True, choices=[])
    tags = forms.CharField(required=False)

    file_cat = forms.ModelChoiceField(label=_("Category"),
                                      queryset=FilesCategory.objects.filter(parent=None),
                                      empty_label="-----------",
                                      required=False)
    file_sub_cat = forms.ModelChoiceField(label=_("Sub-Category"),
                                          queryset=FilesCategory.objects.none(),
                                          empty_label=_("Please choose a category first"),
                                          required=False)

    allow_anonymous_view = forms.BooleanField(label=_("Public can View"), initial=True, required=False)

    group_perms = GroupPermissionField()
    user_perms = UserPermissionField()
    member_perms = MemberPermissionField()

    class Meta:
        fieldsets = (
            (_('File Information'), {
                'fields': ('files',
                           'tags',
                           'group',
                           )
            }),
            (_('Category'), {'fields': ('file_cat', 'file_sub_cat')}),
            (_('Permissions'), {'fields': ('allow_anonymous_view',)}),
            (_('Advanced Permissions'), {'classes': ('collapse',), 'fields': (
                'user_perms',
                'member_perms',
                'group_perms',
            )}),
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        if self.request:
            self.user = self.request.user
        else:
            self.user = None

        super(MultiFileForm, self).__init__(*args, **kwargs)
        default_groups = Group.objects.filter(status=True, status_detail="active")

        if args:
            post_data = args[0]
        else:
            post_data = None

        if self.user and not self.user.profile.is_superuser:
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

        # set up the sub category choices
        if post_data:
            file_cat = post_data.get('file_cat', '0')
            if file_cat and file_cat != '0' and file_cat != u'':
                [file_cat] = FilesCategory.objects.filter(pk=int(file_cat))[:1] or [None]
                if file_cat:
                    self.fields['file_sub_cat'].queryset = FilesCategory.objects.filter(parent=file_cat)

    def clean_user_perms(self):
        user_perm_bits = []
        value = self.cleaned_data['user_perms']
        if value:
            if 'allow_user_view' in value:
                user_perm_bits.append(True)
            else:
                user_perm_bits.append(False)

            if 'allow_user_edit' in value:
                user_perm_bits.append(True)
            else:
                user_perm_bits.append(False)
            value = tuple(user_perm_bits)
        else:
            value = (False, False,)
        return value

    def clean_member_perms(self):
        member_perm_bits = []
        value = self.cleaned_data['member_perms']
        if value:
            if 'allow_member_view' in value:
                member_perm_bits.append(True)
            else:
                member_perm_bits.append(False)

            if 'allow_member_edit' in value:
                member_perm_bits.append(True)
            else:
                member_perm_bits.append(False)
            value = tuple(member_perm_bits)
        else:
            value = (False, False,)
        return value

    def clean_group_perms(self):
        value = self.cleaned_data['group_perms']
        groups_and_perms = []
        if value:
            for item in value:
                perm, group_pk = item.split('_')
                groups_and_perms.append((group_pk, perm,))
            value = tuple(groups_and_perms)
        return value

    def clean_group(self):
        group_id = self.cleaned_data['group']

        try:
            group = Group.objects.get(pk=group_id)
            return group
        except Group.DoesNotExist:
            raise forms.ValidationError(_('Invalid group selected.'))

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        counter = 0

        files = data.get('files')
        tags = data.get('tags')
        group = data.get('group')
        file_cat = data.get('file_cat', None)
        file_sub_cat = data.get('file_sub_cat', None)
        is_public = data.get('allow_anonymous_view', False)

        for new_file in files:
            file = File(
                file=new_file,
                tags=tags,
                group=group,
                allow_anonymous_view=is_public,
                file_cat=file_cat,
                file_sub_cat=file_sub_cat)

            file.save()

            # update all permissions and save the model
            file = update_perms_and_save(self.request, self, file)

            #setup categories
            category = Category.objects.get_for_object(file, 'category')
            sub_category = Category.objects.get_for_object(file, 'sub_category')

            ## update the category of the file
            category_removed = False
            category = file.file_cat.name if file.file_cat else u''

            if category:
                Category.objects.update(file, category, 'category')
            else:  # remove
                category_removed = True
                Category.objects.remove(file, 'category')
                Category.objects.remove(file, 'sub_category')

            if not category_removed:
                # update the sub category of the file
                sub_category = file.file_sub_cat.name if file.file_sub_cat else u''
                if sub_category:
                    Category.objects.update(file, sub_category, 'sub_category')
                else:  # remove
                    Category.objects.remove(file, 'sub_category')

            #Save relationships
            file.save()
            counter += 1

        return counter


class FileCategoryForm(forms.Form):
    """
    Form dedicated on adding category to files
    """

    file_cat = forms.ModelChoiceField(label=_("Category"),
                                      queryset=FilesCategory.objects.filter(parent=None),
                                      empty_label="-----------",
                                      required=False)
    file_sub_cat = forms.ModelChoiceField(label=_("Sub-Category"),
                                          queryset=FilesCategory.objects.none(),
                                          empty_label=_("Please choose a category first"),
                                          required=False)

    def __init__(self, *args, **kwargs):
        super(FileCategoryForm, self).__init__(*args, **kwargs)

        if args:
            post_data = args[0]
        else:
            post_data = None

        if post_data:
            file_cat = post_data.get('file_cat', '0')
            if file_cat and file_cat != '0' and file_cat != u'':
                file_cat = FilesCategory.objects.get(pk=int(file_cat))
                self.fields['file_sub_cat'].queryset = FilesCategory.objects.filter(parent=file_cat)

    def update_file_cat_and_sub_cat(self, file):
        data = self.cleaned_data

        file_cat = data.get('file_cat')
        file_sub_cat = data.get('file_sub_cat')

        file.file_cat = file_cat
        file.file_sub_cat = file_sub_cat

        #setup categories
        category = Category.objects.get_for_object(file, 'category')
        sub_category = Category.objects.get_for_object(file, 'sub_category')

        ## update the category of the file
        category_removed = False
        category = file.file_cat.name if file.file_cat else u''

        if category:
            Category.objects.update(file, category, 'category')
        else:  # remove
            category_removed = True
            Category.objects.remove(file, 'category')
            Category.objects.remove(file, 'sub_category')

        if not category_removed:
            # update the sub category of the file
            sub_category = file.file_sub_cat.name if file.file_sub_cat else u''
            if sub_category:
                Category.objects.update(file, sub_category, 'sub_category')
            else:  # remove
                Category.objects.remove(file, 'sub_category')

        #Save relationships
        file.save()
