from django import forms
from django.utils.translation import ugettext_lazy as _

from museums.models import Museum, Photo
from perms.forms import TendenciBaseForm
from tinymce.widgets import TinyMCE
from base.fields import SplitDateTimeField

class MuseumForm(TendenciBaseForm):
    class Meta:
        model = Museum
    
    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['file']
        
    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Photo")
