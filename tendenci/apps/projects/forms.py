import imghdr
from os.path import splitext, basename
from django import forms
from django.utils.translation import ugettext_lazy as _

from tendenci.apps.projects.models import Project, Photo, TeamMembers, Documents, Category
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)

class ProjectForm(TendenciBaseForm):
    class Meta:
        model = Project
        fields = (
                'project_name',
                'slug',
                'project_number',
                'project_status',
                'category',
                'cost',
                'location',
                'city',
                'state',
                'project_manager',
                'project_description',
                'video_title',
                'video_description',
                'video_embed_code',
                'start_dt',
                'end_dt',
                'resolution',
                'client',
                'tags',
                'website_title',
                'website_url',
                'allow_anonymous_view',
                'user_perms',
                'group_perms',
                'member_perms',
                'status',
                'status_detail',
        )

    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    project_description = forms.CharField(required=False,
        widget=TinyMCE(
            attrs={'style':'width:100%'},
            mce_attrs={
                'storme_app_label':u'projects',
                'storme_model':Project._meta.model_name.lower()
            }))
    video_description = forms.CharField(required=False,
        widget=TinyMCE(
            attrs={'style':'width:100%'},
            mce_attrs={
                'storme_app_label':u'projects',
                'storme_model':Project._meta.model_name.lower()
            }))
    resolution = forms.CharField(required=False,
        widget=TinyMCE(
            attrs={'style':'width:100%'},
            mce_attrs={
                'storme_app_label':u'projects',
                'storme_model':Project._meta.model_name.lower()
            }))

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['project_description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['video_description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['resolution'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['project_description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['video_description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['resolution'].widget.mce_attrs['app_instance_id'] = 0

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'photo_description', 'file']

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Photo")

class DocumentsForm(forms.ModelForm):
    class Meta:
        model = Documents
        fields = ['doc_type', 'document_dt', 'other', 'file']

    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("File")

class TeamMembersForm(forms.ModelForm):
    class Meta:
        model = TeamMembers
        fields = ['first_name', 'last_name', 'title', 'role', 'team_description', 'file']

    def __init__(self, *args, **kwargs):
        super(TeamMembersForm, self).__init__(*args, **kwargs)


class CategoryAdminForm(forms.ModelForm):
    photo_upload = forms.FileField(label=_('Photo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current photo'), required=False)

    class Meta:
        model = Category

        fields = (
            'name',
            'photo_upload',
            'position',
        )

        fieldsets = [('Category', {
                      'fields': ['name',
                                 'photo_upload',
                                 ],
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
        return photo_upload

    def __init__(self, *args, **kwargs):
        super(CategoryAdminForm, self).__init__(*args, **kwargs)
        if self.instance.image:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.image.pk, basename(self.instance.image.file.name))
        else:
            self.fields.pop('remove_photo')

    def save(self, *args, **kwargs):
        category = super(CategoryAdminForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            category.image = None
        return category
