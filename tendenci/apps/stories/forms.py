import imghdr
from os.path import splitext, basename
from datetime import datetime
from datetime import timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from tendenci.apps.stories.models import Story
from tendenci.core.perms.forms import TendenciBaseForm
from tendenci.core.base.fields import SplitDateTimeField
from tendenci.core.files.utils import get_max_file_upload_size
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
    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=END_DT_INITIAL)
    expires = forms.BooleanField(
        label=_('Expires'),
        required=False,
        help_text=_('Check if you want this story to expire and be sure to specify the end date.'),
        initial=False,
    )
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    photo_upload = forms.FileField(label=_('Photo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current photo'), required=False)
    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True, status_detail="active"), required=True, empty_label=None)

    class Meta:
        model = Story

        fields = (
            'title',
            'content',
            'full_story_link',
            'link_title',
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

        fieldsets = [('Story Information', {
                      'fields': ['title',
                                 'content',
                                 'photo_upload',
                                 'full_story_link',
                                 'link_title',
                                 'tags',
                                 'start_dt',
                                 'end_dt',
                                 'expires',
                                 'group',
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
                raise forms.ValidationError('The photo must be of jpg, gif, or png image type.')
            
            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo is an invalid image. Try uploading another photo.')

            max_upload_size = get_max_file_upload_size()
            if photo_upload.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(photo_upload.size)))

        return photo_upload
                 
    def __init__(self, *args, **kwargs):
        super(StoryForm, self).__init__(*args, **kwargs)
        self.fields['group'].initial = Group.objects.get_initial_group_id()
        if self.instance.image:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.image.pk, basename(self.instance.image.file.name))
        else:
            self.fields.pop('remove_photo')
        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

    def save(self, *args, **kwargs):
        story = super(StoryForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            story.image = None
        return story


class StoryAdminForm(TendenciBaseForm):
    start_dt = SplitDateTimeField(label=_('Start Date/Time'), initial=datetime.now())
    end_dt = SplitDateTimeField(label=_('End Date/Time'), initial=END_DT_INITIAL)
    expires = forms.BooleanField(
        label=_('Expires'),
        required=False,
        help_text=_('Check if you want this story to expire and be sure to specify the end date.'),
        initial=False,
    )
    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    photo_upload = forms.FileField(label=_('Photo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current photo'), required=False)

    class Meta:
        model = Story

        fields = (
            'title',
            'content',
            'full_story_link',
            'link_title',
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

        fieldsets = [('Story Information', {
                      'fields': ['title',
                                 'content',
                                 'photo_upload',
                                 'full_story_link',
                                 'link_title',
                                 'tags',
                                 'start_dt',
                                 'end_dt',
                                 'expires'
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
                raise forms.ValidationError('The photo must be of jpg, gif, or png image type.')

            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The photo is an invalid image. Try uploading another photo.')

            max_upload_size = get_max_file_upload_size()
            if photo_upload.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(photo_upload.size)))

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
