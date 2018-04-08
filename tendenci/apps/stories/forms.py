import imghdr
from os.path import splitext, basename
from datetime import datetime
from datetime import timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from tendenci.apps.stories.models import Story
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.files.utils import get_max_file_upload_size
from tendenci.apps.perms.utils import get_query_filters
from tendenci.apps.user_groups.models import Group

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)

END_DT_INITIAL = datetime.now() + timedelta(weeks=2)


class StoryForm(TendenciBaseForm):
    fullstorylink = forms.CharField(label=_("Full Story Link"), required=False, max_length=300)
    start_dt = forms.SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = forms.SplitDateTimeField(label=_('End Date/Time'), initial=END_DT_INITIAL)
    expires = forms.BooleanField(
        label=_('Expires'),
        required=False,
        help_text=_('Check if you want this story to expire and be sure to specify the end date.'),
        initial=False,
    )
    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)
    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))
    photo_upload = forms.FileField(label=_('Photo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current photo'), required=False)
    group = forms.ChoiceField(required=True, choices=[])

    class Meta:
        model = Story

        fields = (
            'title',
            'content',
            'full_story_link',
            'link_title',
            'video_embed_url',
            'rotator',
            'tags',
            'photo_upload',
            'start_dt',
            'end_dt',
            'expires',
            'group',
            'syndicate',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status_detail',
        )

        fieldsets = [(_('Story Information'), {
                      'fields': ['title',
                                 'content',
                                 'photo_upload',
                                 'video_embed_url',
                                 'full_story_link',
                                 'link_title',
                                 'rotator',
                                 'tags',
                                 'start_dt',
                                 'end_dt',
                                 'expires',
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
                      'fields': ['syndicate',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def clean_photo_upload(self):
        photo_upload = self.cleaned_data['photo_upload']
        if photo_upload:
            extension = splitext(photo_upload.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError(_('The photo must be of jpg, gif, or png image type.'))

            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError(_('The photo is an invalid image. Try uploading another photo.'))

            max_upload_size = get_max_file_upload_size()
            if photo_upload.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %(max_upload_size)s. Current filesize %(upload_size)s') % {
                                            'max_upload_size': filesizeformat(max_upload_size),
                                            'upload_size': filesizeformat(photo_upload.size)})

        return photo_upload

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

    def __init__(self, *args, **kwargs):
        super(StoryForm, self).__init__(*args, **kwargs)
        if self.instance.image:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.image.pk, basename(self.instance.image.file.name))
        else:
            self.fields.pop('remove_photo')

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

    def save(self, *args, **kwargs):
        story = super(StoryForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            story.image = None
        return story


class StoryAdminForm(TendenciBaseForm):
    start_dt = forms.SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = forms.SplitDateTimeField(label=_('End Date/Time'), initial=END_DT_INITIAL)
    expires = forms.BooleanField(
        label=_('Expires'),
        required=False,
        help_text=_('Check if you want this story to expire and be sure to specify the end date.'),
        initial=False,
    )
    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)
    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))
    photo_upload = forms.FileField(label=_('Photo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current photo'), required=False)

    class Meta:
        model = Story

        fields = (
            'title',
            'content',
            'full_story_link',
            'link_title',
            'video_embed_url',
            'rotator',
            'tags',
            'photo_upload',
            'start_dt',
            'end_dt',
            'expires',
            'syndicate',
            'allow_anonymous_view',
            'user_perms',
            'member_perms',
            'group_perms',
            'status_detail',
        )

        fieldsets = [(_('Story Information'), {
                      'fields': ['title',
                                 'content',
                                 'photo_upload',
                                 'video_embed_url',
                                 'full_story_link',
                                 'link_title',
                                 'rotator',
                                 'tags',
                                 'start_dt',
                                 'end_dt',
                                 'expires'
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
                      'fields': ['syndicate',
                                 'status_detail'],
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

    def clean_photo_upload(self):
        photo_upload = self.cleaned_data['photo_upload']
        if photo_upload:
            extension = splitext(photo_upload.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError(_('The photo must be of jpg, gif, or png image type.'))

            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError(_('The photo is an invalid image. Try uploading another photo.'))

            max_upload_size = get_max_file_upload_size()
            if photo_upload.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %(max_upload_size)s. Current filesize %(upload_size)s') % {
                                            'max_upload_size': filesizeformat(max_upload_size),
                                            'upload_size': filesizeformat(photo_upload.size)})

        return photo_upload

    def __init__(self, *args, **kwargs):
        super(StoryAdminForm, self).__init__(*args, **kwargs)
        if self.instance.image:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.image.pk, basename(self.instance.image.file.name))
        else:
            self.fields.pop('remove_photo')

    def save(self, *args, **kwargs):
        story = super(StoryAdminForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            story.image = None
        return story


class UploadStoryImageForm(forms.Form):
    file  = forms.FileField(label=_("File Path"))
