from django import forms

from models import Video
from tinymce.widgets import TinyMCE
from perms.forms import TendenciBaseForm
from embedly import is_pattern_match

class VideoForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Video._meta.app_label, 
        'storme_model':Video._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))
    
    class Meta:
        model = Video

    def __init__(self, *args, **kwargs): 
        super(VideoForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
            
    def clean_video_url(self):
        value = self.cleaned_data.get('video_url')
        if not value:
            return value
        if not is_pattern_match(value):
            raise forms.ValidationError('This url is not supported by embed.ly')
        return value