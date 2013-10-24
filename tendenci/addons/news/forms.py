import imghdr
from os.path import splitext, basename
from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from tendenci.addons.news.models import News
from tendenci.core.perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from tendenci.core.base.fields import SplitDateTimeField
from tendenci.core.base.fields import EmailVerificationField
from tendenci.core.files.utils import get_max_file_upload_size
from tendenci.apps.user_groups.models import Group

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)


class NewsForm(TendenciBaseForm):
    body = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style': 'width:100%;'},
        mce_attrs={'storme_app_label': News._meta.app_label,
        'storme_model': News._meta.module_name.lower()}))
    release_dt = SplitDateTimeField(label=_('Release Date/Time'), initial=datetime.now())
    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending')))
    email = EmailVerificationField(label=_("Email"), required=False)

    photo_upload = forms.FileField(label=_('Thumbnail Image'), required=False, help_text=_('The thumbnail image can be used on your homepage or sidebar if it is setup in your theme. It will not display on the news page.'))
    remove_photo = forms.BooleanField(label=_('Remove the current photo'), required=False)

    group = forms.ModelChoiceField(queryset=Group.objects.filter(status=True, status_detail="active"), required=True, empty_label=None)

    class Meta:
        model = News

        fields = (
        'headline',
        'slug',
        'summary',
        'body',
        'group',
        'photo_upload',
        'source',
        'website',
        'release_dt',
        'timezone',
        'first_name',
        'last_name',
        'phone',
        'fax',
        'email',
        'tags',
        'allow_anonymous_view',
        'syndicate',
        'user_perms',
        'member_perms',
        'group_perms',
        'status_detail',
        )

        fieldsets = [('News Information', {
                      'fields': ['headline',
                                 'slug',
                                 'summary',
                                 'body',
                                 'group',
                                 'tags',
                                 'photo_upload',
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

    def save(self, *args, **kwargs):
        news = super(NewsForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            news.thumbnail = None
        return news

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['body'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['group'].initial = Group.objects.get_initial_group_id()

        #if not self.user.profile.is_superuser:
        if self.user and not self.user.profile.is_superuser:
            if 'status_detail' in self.fields:
                self.fields.pop('status_detail')

        # only show the remove photo checkbox if there is already a thumbnail
        if self.instance.thumbnail:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.thumbnail.pk, basename(self.instance.thumbnail.file.name))
        else:
            self.fields.pop('remove_photo')
