from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from django.template.defaultfilters import filesizeformat

from tendenci.core.categories.forms import (CategoryForm, CategoryField, category_defaults,
    sub_category_defaults)

from tendenci.core.categories.models import CategoryItem, Category
from tendenci.core.files.fields import MultiFileField
from tendenci.core.files.models import File
from tendenci.core.files.utils import get_max_file_upload_size
from tendenci.core.perms.fields import GroupPermissionField, groups_with_perms, UserPermissionField, MemberPermissionField, group_choices
from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.core.perms.object_perms import ObjectPermission
from tendenci.core.perms.utils import update_perms_and_save, get_query_filters
from tendenci.apps.user_groups.models import Group
from form_utils.forms import BetterForm


class FileForm(TendenciBaseForm):

    group = forms.ChoiceField(required=True, choices=[])

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

                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),

                     ('Administrator Only', {
                      'fields': ['status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        default_groups = Group.objects.filter(status=True, status_detail="active")

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

    def clean_file(self):
        data = self.cleaned_data.get('file')
        max_upload_size = get_max_file_upload_size(file_module=True)
        if data.size > max_upload_size:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(data.size)))

        return data

    def clean_group(self):
        group_id = self.cleaned_data['group']

        try:
            group = Group.objects.get(pk=group_id)
            return group
        except Group.DoesNotExist:
            raise forms.ValidationError(_('Invalid group selected.'))


class SwfFileForm(TendenciBaseForm):

    class Meta:
        model = File

        fields = (
            'file',
            'name',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status',
        )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            self.user = None

        super(SwfFileForm, self).__init__(*args, **kwargs)


class MostViewedForm(forms.Form):
    """
    Takes in the date range and files type you're
    searching for and returns back a result list.
    """

    TYPES = (
      ('all', 'All File Types'),
      ('pdf', 'PDF Documents'),
      ('slides', 'Slides'),
      ('spreadsheet', 'Spreadsheets'),
      ('text', 'Text Documents'),
      ('zip', 'Zip Files'),
    )

    start_dt = forms.DateField(label='Start')
    end_dt = forms.DateField(label='End')
    file_type = forms.ChoiceField(label='File Type', choices=TYPES)

    def __init__(self, *args, **kwargs):
        super(MostViewedForm, self).__init__(*args, **kwargs)
        self.fields['file_type'].widget.attrs['class'] = 'btn'


class FileSearchForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    category = CategoryField(label=_('Category'), choices=[], required=False)
    sub_category = CategoryField(label=_('Sub Category'), choices=[], required=False)
    group = forms.ChoiceField(label=_('Group'), choices=[], required=False)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        else:
            self.user = None

        super(FileSearchForm, self).__init__(*args, **kwargs)

        user = self.user or AnonymousUser()
        filters = get_query_filters(user, 'user_groups.view_group', **{'perms_field': False})
        groups = Group.objects.filter(filters).distinct()
        groups_list = [[g.id, g.name] for g in groups]
        if user.is_authenticated():
            users_groups = self.user.profile.get_groups()
            for g in users_groups:
                if [g.id, g.name] not in groups_list:
                    groups_list.append([g.id, g.name])

        groups_list.insert(0, ['', '------------'])
        self.fields['group'].choices = tuple(groups_list)

        content_type = ContentType.objects.get(app_label='files', model='file')
        categories = CategoryItem.objects.filter(content_type=content_type,
                                                 parent__exact=None)
        categories = list(set([cat.category.name for cat in categories]))
        categories = [[cat, cat] for cat in categories]
        categories.insert(0, ['', '------------'])
        self.fields['category'].choices = tuple(categories)

        # set up the sub category choices
        sub_categories = CategoryItem.objects.filter(content_type=content_type,
                                                     category__exact=None)
        sub_categories = list(set([cat.parent.name for cat in sub_categories]))
        sub_categories = [[cat, cat] for cat in sub_categories]
        sub_categories.insert(0, ['', '------------'])
        self.fields['sub_category'].choices = tuple(sub_categories)


class FilewithCategoryForm(TendenciBaseForm):

    group = forms.ChoiceField(required=True, choices=[])

    category = CategoryField(required=False, **category_defaults)
    sub_category = CategoryField(required=False, **sub_category_defaults)

    class Meta:
        model = File

        fields = (
            'file',
            'name',
            'group',
            'tags',
            'category',
            'sub_category',
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

        content_type = ContentType.objects.get(app_label='files', model='file')
        categories = CategoryItem.objects.filter(content_type=content_type,
                                                 parent__exact=None)
        categories = list(set([cat.category.name for cat in categories]))
        categories = [[cat, cat] for cat in categories]
        categories.insert(0, [0, '------------'])
        if post_data:
            new_category = post_data.get('category','0')
            if new_category != '0':
                categories.append([new_category,new_category])
        self.fields['category'].choices = tuple(categories)

        # set up the sub category choices
        sub_categories = CategoryItem.objects.filter(content_type=content_type,
                                                     category__exact=None)
        sub_categories = list(set([cat.parent.name for cat in sub_categories]))
        sub_categories = [[cat, cat] for cat in sub_categories]
        sub_categories.insert(0, [0, '------------'])
        if post_data:
            new_sub_category = post_data.get('sub_category','0')
            if new_sub_category != '0':
                sub_categories.append([new_sub_category,new_sub_category])
        self.fields['sub_category'].choices = tuple(sub_categories)

        if self.instance and self.instance.pk:
            category = Category.objects.get_for_object(self.instance, 'category')
            sub_category = Category.objects.get_for_object(self.instance, 'sub_category')
            self.fields['category'].initial = category
            self.fields['sub_category'].initial = sub_category


    def clean_file(self):
        data = self.cleaned_data.get('file')
        max_upload_size = get_max_file_upload_size(file_module=True)
        if data.size > max_upload_size:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(data.size)))

        return data

    def clean_group(self):
        group_id = self.cleaned_data['group']

        try:
            group = Group.objects.get(pk=group_id)
            return group
        except Group.DoesNotExist:
            raise forms.ValidationError(_('Invalid group selected.'))

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        file = super(FilewithCategoryForm, self).save(*args, **kwargs)

        file.save()

        #setup categories
        category = Category.objects.get_for_object(file, 'category')
        sub_category = Category.objects.get_for_object(file, 'sub_category')

        ## update the category of the file
        category_removed = False
        category = data.get('category')

        if category != '0':
            Category.objects.update(file, category, 'category')
        else:  # remove
            category_removed = True
            Category.objects.remove(file, 'category')
            Category.objects.remove(file, 'sub_category')

        if not category_removed:
            # update the sub category of the article
            sub_category = data.get('sub_category')
            if sub_category != '0':
                Category.objects.update(file, sub_category, 'sub_category')
            else:  # remove
                Category.objects.remove(file, 'sub_category')

        #Save relationships
        file.save()

        return file


class MultiFileForm(BetterForm):
    files = MultiFileField(min_num=1)
    group = forms.ChoiceField(required=True, choices=[])
    tags = forms.CharField(required=False)

    category = CategoryField(required=False, **category_defaults)
    sub_category = CategoryField(required=False, **sub_category_defaults)

    allow_anonymous_view = forms.BooleanField(label=_("Public can View"), initial=True, required=False)

    group_perms = GroupPermissionField()
    user_perms = UserPermissionField()
    member_perms = MemberPermissionField()

    class Meta:
        fieldsets = (
            ('File Information', {
                'fields': ('files',
                           'tags',
                           'group',
                           )
            }),
            ('Category', {'fields': ('category', 'sub_category')}),
            ('Permissions', {'fields': ('allow_anonymous_view',)}),
            ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
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

        content_type = ContentType.objects.get(app_label='files', model='file')
        categories = CategoryItem.objects.filter(content_type=content_type,
                                                 parent__exact=None)
        categories = list(set([cat.category.name for cat in categories]))
        categories = [[cat, cat] for cat in categories]
        categories.insert(0, [0, '------------'])
        if post_data:
            new_category = post_data.get('category','0')
            if new_category != '0':
                categories.append([new_category,new_category])
        self.fields['category'].choices = tuple(categories)

        # set up the sub category choices
        sub_categories = CategoryItem.objects.filter(content_type=content_type,
                                                     category__exact=None)
        sub_categories = list(set([cat.parent.name for cat in sub_categories]))
        sub_categories = [[cat, cat] for cat in sub_categories]
        sub_categories.insert(0, [0, '------------'])
        if post_data:
            new_sub_category = post_data.get('sub_category','0')
            if new_sub_category != '0':
                sub_categories.append([new_sub_category,new_sub_category])
        self.fields['sub_category'].choices = tuple(sub_categories)

    def clean_files(self):
        files = self.cleaned_data.get('files')
        max_upload_size = get_max_file_upload_size(file_module=True)
        for data in files:
            if data.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(data.size)))

        return files

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
        category_from_form = data.get('category')
        sub_category_from_form = data.get('sub_category')
        is_public = data.get('allow_anonymous_view', False)

        for new_file in files:
            file = File(file=new_file, tags=tags, group=group, allow_anonymous_view=is_public)
            file.save()

            # update all permissions and save the model
            file = update_perms_and_save(self.request, self, file)

            #setup categories
            category = Category.objects.get_for_object(file, 'category')
            sub_category = Category.objects.get_for_object(file, 'sub_category')

            ## update the category of the file
            category_removed = False
            category = category_from_form

            if category != '0':
                Category.objects.update(file, category, 'category')
            else:  # remove
                category_removed = True
                Category.objects.remove(file, 'category')
                Category.objects.remove(file, 'sub_category')

            if not category_removed:
                # update the sub category of the file
                sub_category = sub_category_from_form
                if sub_category != '0':
                    Category.objects.update(file, sub_category, 'sub_category')
                else:  # remove
                    Category.objects.remove(file, 'sub_category')

            #Save relationships
            file.save()
            counter += 1

        return counter


class FileCategoryForm(CategoryForm):
    """
    Form dedicated on adding category to files
    """

    category = CategoryField(required=False, **category_defaults)
    sub_category = CategoryField(required=False, **sub_category_defaults)

    def __init__(self, content_type, *args, **kwargs):
        super(FileCategoryForm, self).__init__(content_type, *args, **kwargs)

        self.fields['category'].help_text = mark_safe('<a href="#" class="add-category">+</a>')
        self.fields['sub_category'].help_text = mark_safe('<a href="#" class="add-sub-category">+</a>')

        del self.fields['app_label']
        del self.fields['model']
        del self.fields['pk']

    def update_file_cat_and_sub_cat(self, file):
        data = self.cleaned_data

        category_from_form = data.get('category')
        sub_category_from_form = data.get('sub_category')

        #setup categories
        category = Category.objects.get_for_object(file, 'category')
        sub_category = Category.objects.get_for_object(file, 'sub_category')

        ## update the category of the file
        category_removed = False
        category = category_from_form

        if category != '0':
            Category.objects.update(file, category, 'category')
        else:  # remove
            category_removed = True
            Category.objects.remove(file, 'category')
            Category.objects.remove(file, 'sub_category')

        if not category_removed:
            # update the sub category of the file
            sub_category = sub_category_from_form
            if sub_category != '0':
                Category.objects.update(file, sub_category, 'sub_category')
            else:  # remove
                Category.objects.remove(file, 'sub_category')

        #Save relationships
        file.save()