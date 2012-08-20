import imghdr
from os.path import splitext, basename

from tendenci.apps.pages.models import Page
from tendenci.core.perms.forms import TendenciBaseForm
from django import forms
from django.utils.translation import ugettext_lazy as _

from tinymce.widgets import TinyMCE
from tendenci.core.base.utils import get_template_list

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
        choices=(('active','Active'), ('inactive','Inactive'), ('pending','Pending'), ('archive','Archive')))

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
        
        # By default all pages other than the newly creted version is set to archive
        set_others_to_archive = True
        # Only the superuser has the power to override this feature
        if self.user.profile.is_superuser:
            # The superuser sets the page to deleted
            if not self.cleaned_data.get('status'):
                set_others_to_archive = False
            # The superuser did not set the newly created version to active
            elif not self.cleaned_data.get('status_detail') == 'active':
                set_others_to_archive = False
        print 'set_others_to_archive', set_others_to_archive

        if set_others_to_archive:
            # Set status of other versions to archive
            pages = Page.objects.filter(guid=page.guid, status_detail='active').exclude(status=False)
            for p in pages:
                p.status_detail = 'archive'
                p.save()

        if self.cleaned_data.get('remove_photo'):
            page.header_image = None

        if page.pk:
            # Clone page foreign key
            if page.header_image:
                header_image_clone = page.header_image
                header_image_clone.pk = None
                header_image_clone.save()
                page.header_image = header_image_clone
            if page.entity:
                entity_clone = page.entity
                entity_clone.pk = None
                entity_clone.save()
                page.entity = entity_clone
            if page.meta:
                meta_clone = page.meta
                meta_clone.pk = None
                meta_clone.save()
                page.meta = meta_clone
            
            # Set current page to active if other pages are set to archive
            if set_others_to_archive:
                page.status = True
                page.status_detail = 'active'
            # Clone page
            page.pk = None
            page.save()

        return page
        
class ChangeVersionForm(forms.Form):
    version = forms.ModelChoiceField(queryset=Page.objects.all())

    def __init__(self, page=None, *args, **kwargs):
        super(ChangeVersionForm, self).__init__(*args, **kwargs)
		
		# Initialize version
        self.page = page
        if self.page:
            pages = Page.objects.filter(guid=self.page.guid)
            self.fields['version'].choices = [(p.pk, p.version) for p in pages]
            self.fields['version'].initial = self.page.pk
                

    def save(self, *args, **kwargs):
        if self.page and self.cleaned_data.get('version'):
            print 'cleaned_data = ', self.cleaned_data.get('version')
            # Set other versions to archive
            pages = Page.objects.filter(guid=self.page.guid, status_detail='active').exclude(status=False)
            for p in pages:
                p.status_detail = 'archive'
                p.save()
            version = self.cleaned_data.get('version')
            version.status = True
            version.status_detail = 'active'
            version.save()
        return self.page
