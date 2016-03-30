import imghdr
from os.path import splitext, basename
from django import forms
from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.testimonials.models import Testimonial

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png' 
)

class TestimonialForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('active','Active'),('inactive','Inactive')))
    photo_upload = forms.FileField(label=('Photo'), required=False)
    remove_photo = forms.BooleanField(label=('Remove the current photo'), required=False)

    new_mce_attrs = {
        'plugins': "paste",
        'theme_advanced_buttons1': "bold,italic,|,link,unlink,|,pastetext,|,undo,redo",
        'theme_advanced_buttons2': "",
        'theme_advanced_buttons3': "",
    }
    testimonial = forms.CharField(
        widget=TinyMCE(attrs={'style':'width:100%'},
                       mce_attrs=new_mce_attrs), required=False)

    class Meta:
        model = Testimonial
        fields = (
            'first_name',
            'last_name',
            'photo_upload',
            'testimonial',
            'tags',
            'city',
            'state',
            'country',
            'email',
            'company',
            'title',
            'website',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status',
            'status_detail',
        )

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
        super(TestimonialForm, self).__init__(*args, **kwargs)
        if self.instance.image:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.image.pk, basename(self.instance.image.file.name))
        else:
            self.fields.pop('remove_photo')

    def save(self, *args, **kwargs):
        testimonial = super(TestimonialForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            testimonial.image = None
            testimonial.save()
        return testimonial
