import imghdr
from os.path import splitext, basename

from pages.models import Page
from perms.utils import is_admin
from perms.forms import TendenciBaseForm
from django import forms
from django.utils.translation import ugettext_lazy as _

from tinymce.widgets import TinyMCE
from base.utils import get_template_list

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
        'status',
        'status_detail',
        )
        
    def __init__(self, *args, **kwargs): 
        super(PageAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
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
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

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
        
        if not is_admin(self.user):
            if 'syndicate' in self.fields: self.fields.pop('syndicate')
            if 'status' in self.fields: self.fields.pop('status')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

    def save(self, *args, **kwargs):
        page = super(PageForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            page.header_image = None
        return page
