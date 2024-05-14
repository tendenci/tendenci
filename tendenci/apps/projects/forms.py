import imghdr
from os.path import splitext, basename
from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import inlineformset_factory

#from tendenci.libs.form_utils.forms import BetterModelForm
from tendenci.apps.projects.models import Project, Photo, TeamMembers, Documents, Category
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.files.validators import FileValidator
from tendenci.apps.site_settings.utils import get_setting

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)


class ProjectSearchForm(FormControlWidgetMixin, forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    category = forms.ModelChoiceField(label=_("Category"),
                                      queryset=None,
                                      required=False)

    def __init__(self, *args, **kwargs):
        super(ProjectSearchForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()


class ProjectForm(TendenciBaseForm):
    class Meta:
        model = Project
        fields = (
                'project_name',
                'slug',
                'company_name',
                'start_dt',
                'end_dt',
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
                'resolution',
                'client',
                'group',
                'tags',
                'website_title',
                'website_url',
                'allow_anonymous_view',
                'user_perms',
                'group_perms',
                'member_perms',
                'featured',
                'status_detail',
        )
        
        fieldsets = (
        (None,
            {'fields': (
                'project_name',
                'slug',
                'company_name',
                'start_dt',
                'end_dt',
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
                'resolution',
                'client',
                'website_url',
                'website_title',
                'group',
                'tags'
            )}
        ),
        (_('Permissions'), {
          'fields': ['allow_anonymous_view',
                     'user_perms',
                     'member_perms',
                     'group_perms',
                     ],
          'classes': ['permissions'],
          }),
         (_('Administrator Only'), {
          'fields': ['featured', 'status_detail'],
          'classes': ['admin-only'],
        })
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
        self.request_user = kwargs.pop('request_user', None)
        super(ProjectForm, self).__init__(*args, **kwargs)

        self.fields['project_name'].label = get_setting('module', 'projects', 'projectnamelabel') or _('Project Name')
        self.fields['company_name'].label = get_setting('module', 'projects', 'companynamelabel') or _('Company Name')
        self.fields['allow_anonymous_view'].initial = False
        if self.request_user:
            if not self.request_user.is_superuser:
                del self.fields['allow_anonymous_view']
                del self.fields['user_perms']
                del self.fields['member_perms']
                del self.fields['group_perms']
                del self.fields['status_detail']
                del self.fields['featured']
            
        if self.instance.pk:
            self.fields['project_description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['video_description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            self.fields['resolution'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['project_description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['video_description'].widget.mce_attrs['app_instance_id'] = 0
            self.fields['resolution'].widget.mce_attrs['app_instance_id'] = 0


class ProjectFrontForm(ProjectForm):

    def __init__(self, *args, **kwargs):
        super(ProjectFrontForm, self).__init__(*args, **kwargs)
        exclude_fields = get_setting('module', 'projects', 'excludefields').split(',')
        for field_name in exclude_fields:
            field_name = field_name.strip()
            if field_name in self.fields:
                del self.fields[field_name]


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'photo_description', 'file']

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Photo")
        self.fields['file'].validators = [FileValidator(allowed_extensions=ALLOWED_LOGO_EXT)]
        self.fields['file'].widget.attrs.update({'accept': "image/*"})


class PhotoFrontForm(FormControlWidgetMixin, PhotoForm):

    def __init__(self, *args, **kwargs):
        super(PhotoFrontForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = False
        del self.fields['photo_description']
        #self.fields['file'].required = False


PhotoFormSet = inlineformset_factory(
    Project, Photo, form=PhotoFrontForm,
    max_num=5, validate_max=True,
    extra=1, can_delete=True, can_delete_extra=True
)


class DocumentsForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = Documents
        fields = ['doc_type', 'document_dt', 'other', 'file']

    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("File")
        self.fields['file'].validators = [FileValidator()]
        

class DocumentsFrontForm(DocumentsForm):

    def __init__(self, *args, **kwargs):
        super(DocumentsFrontForm, self).__init__(*args, **kwargs)
        self.fields['document_dt'].widget.attrs.update({'class': "form-control documents-date"})
        del self.fields['doc_type']
        del self.fields['other']


DocumentsFormSet = inlineformset_factory(
    Project, Documents, form=DocumentsFrontForm,
    max_num=3, validate_max=True,
    extra=1, can_delete=True, can_delete_extra=True
)


class TeamMembersForm(FormControlWidgetMixin, forms.ModelForm):
    class Meta:
        model = TeamMembers
        fields = ['first_name', 'last_name', 'title', 'email', 'phone', 'role', 'team_description', 'file']

    def __init__(self, *args, **kwargs):
        super(TeamMembersForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Picture")
        self.fields['file'].validators = [FileValidator(allowed_extensions=ALLOWED_LOGO_EXT)]
        self.fields['file'].widget.attrs.update({'accept': "image/*"})


class TeamMembersFrontForm(TeamMembersForm):

    def __init__(self, *args, **kwargs):
        super(TeamMembersFrontForm, self).__init__(*args, **kwargs)
        del self.fields['role']
        del self.fields['team_description']


TeamMembersFormSet = inlineformset_factory(
    Project, TeamMembers, form=TeamMembersFrontForm,
    max_num=3, validate_max=True,
    extra=1, can_delete=True, can_delete_extra=True
)


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
