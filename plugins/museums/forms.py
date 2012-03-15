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
    about = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Museum._meta.app_label, 
        'storme_model':Museum._meta.module_name.lower()}))

    def __init__(self, *args, **kwargs):
        super(MuseumForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['about'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['about'].widget.mce_attrs['app_instance_id'] = 0

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['file']
        
    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = _("Photo")
