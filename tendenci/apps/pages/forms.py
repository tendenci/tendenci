import imghdr
from os.path import splitext, basename

from tendenci.apps.pages.models import Page
from tendenci.core.perms.forms import TendenciBaseForm

from django.utils.safestring import mark_safe
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from tinymce.widgets import TinyMCE
from tendenci.core.base.utils import get_template_list
from tendenci.core.files.utils import get_max_file_upload_size

template_choices = [('default.html','Default')]
template_choices += get_template_list()

ALLOWED_IMG_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png' 
)

class PageAdminForm(TendenciBaseForm):
    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Page._meta.app_label, 
        'storme_model':Page._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))
    
    template = forms.ChoiceField(choices=template_choices)

    meta_title = forms.CharField(required=False)
    meta_description = forms.CharField(required=False,
        widget=forms.widgets.Textarea(attrs={'style':'width:100%'}))
    meta_keywords = forms.CharField(required=False,
        widget=forms.widgets.Textarea(attrs={'style':'width:100%'}))
    meta_canonical_url = forms.CharField(required=False)

    class Meta:
        model = Page
        fields = (
        'title',
        'slug',
        'content',
        'tags',
        'template',
        'meta_title',
        'meta_description',
        'meta_keywords',
        'meta_canonical_url',
        'allow_anonymous_view',
        'user_perms',
        'group_perms',
        'member_perms',
        'syndicate',
        'status',
        'status_detail',
        )
        
    def __init__(self, *args, **kwargs): 
        super(PageAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            if self.instance.meta:
                self.fields['meta_title'].initial = self.instance.meta.title
                self.fields['meta_description'].initial = self.instance.meta.description
                self.fields['meta_keywords'].initial = self.instance.meta.keywords
                self.fields['meta_canonical_url'].initial = self.instance.meta.canonical_url
        else:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0
        
        template_choices = [('default.html','Default')]
        template_choices += get_template_list()
        self.fields['template'].choices = template_choices


class PageForm(TendenciBaseForm):
    header_image = forms.ImageField(required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current header image'), required=False)

    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Page._meta.app_label, 
        'storme_model':Page._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending')))

    tags = forms.CharField(required=False, help_text=mark_safe('<a href="/tags/" target="_blank">Open All Tags list in a new window</a>'))

    template = forms.ChoiceField(choices=template_choices)
    
    class Meta:
        model = Page
        fields = (
        'title',
        'slug',
        'content',
        'tags',
        'template',
        'allow_anonymous_view',
        'syndicate',
        'user_perms',
        'group_perms',
        'member_perms',
        'status',
        'status_detail',
        )

        fieldsets = [('Page Information', {
                      'fields': ['title',
                                 'slug',
                                 'content',
                                 'tags',
                                 'header_image',
                                 'template',
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
                                 'status',
                                 'status_detail'], 
                      'classes': ['admin-only'],
                    })]

    def clean(self):
        cleaned_data = super(PageForm, self).clean()
        slug = cleaned_data.get('slug')

        # Check if duplicate slug from different page (i.e. different guids)
        # Case 1: Page is edited
        if self.instance:
            guid = self.instance.guid
            if Page.objects.filter(slug=slug).exclude(guid=guid).exists():
                self._errors['slug'] = self.error_class(['Duplicate value for slug.'])
                del cleaned_data['slug']
        # Case 2: Add new Page
        else:
            if Page.objects.filter(slug=slug).exists():
                self._errors['slug'] = self.error_class(['Duplicate value for slug.'])
                del cleaned_data['slug']

        return cleaned_data    
    
    def clean_header_image(self):
        header_image = self.cleaned_data['header_image']
        if header_image:
            extension = splitext(header_image.name)[1]
            
            # check the extension
            if extension.lower() not in ALLOWED_IMG_EXT:
                raise forms.ValidationError('The header image must be of jpg, gif, or png image type.')
            
            # check the image header_image
            image_type = '.%s' % imghdr.what('', header_image.read())
            if image_type not in ALLOWED_IMG_EXT:
                raise forms.ValidationError('The header image is an invalid image. Try uploading another image.')

            max_upload_size = get_max_file_upload_size()
            if header_image.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(header_image.size)))

        return header_image

    def __init__(self, *args, **kwargs): 
        super(PageForm, self).__init__(*args, **kwargs)
        if self.instance.header_image:
            self.fields['header_image'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.header_image.pk, basename(self.instance.header_image.file.name))
        else:
            self.fields.pop('remove_photo')

        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0
        
        template_choices = [('default.html','Default')]
        template_choices += get_template_list()
        self.fields['template'].choices = template_choices
        
        if not self.user.profile.is_superuser:
            if 'syndicate' in self.fields: self.fields.pop('syndicate')
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

    def save(self, *args, **kwargs):
        page = super(PageForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            page.header_image = None
        return page
