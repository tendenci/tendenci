from os.path import splitext, basename
from django import forms
from tendenci.libs.tinymce.widgets import TinyMCE

from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.testimonials.models import Testimonial
from tendenci.apps.files.validators import FileValidator

ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)

class TestimonialForm(TendenciBaseForm):
    status_detail = forms.ChoiceField(choices=(('active','Active'),('inactive','Inactive')))
    photo_upload = forms.ImageField(label=('Photo'), required=False)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.image:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/{}/">{}</a>'.format(self.instance.image.pk, basename(self.instance.image.file.name))
        else:
            self.fields.pop('remove_photo')
        if 'photo_upload' in self.fields:
            self.fields['photo_upload'].validators = [FileValidator(allowed_extensions=ALLOWED_LOGO_EXT)]

    def save(self, *args, **kwargs):
        testimonial = super().save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            testimonial.image = None
            testimonial.save()
        return testimonial
