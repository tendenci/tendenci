from django import forms

from tendenci.apps.videos.models import Video
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.perms.forms import TendenciBaseForm
from embedly import Embedly

# Create Embedly instance
client = Embedly("438be524153e11e18f884040d3dc5c07")

class VideoForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Video._meta.app_label, 
        'storme_model':Video._meta.model_name.lower()}))

    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))

    clear_image = forms.BooleanField(required=False)

    class Meta:
        model = Video
        fields = (
            'title',
            'slug',
            'category',
            'video_type',
            'image',
            'video_url',
            'tags',
            'description',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status_detail',
        )

    def __init__(self, *args, **kwargs): 
        super(VideoForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
            
    def clean_video_url(self):
        value = self.cleaned_data.get('video_url')
        # Get embedded object from URL
        obj = client.oembed(value)
        if not value:
            raise forms.ValidationError('You must enter a URL')
        if obj.get('error'):
            raise forms.ValidationError('This url is not supported by embed.ly')
        return value

    def save(self, *args, **kwargs):
        video = super(VideoForm, self).save(*args, **kwargs)
        if self.cleaned_data['clear_image']:
            video.image.delete()
        return video
