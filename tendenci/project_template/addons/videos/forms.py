from django import forms

from addons.videos.models import Video
from tinymce.widgets import TinyMCE
from tendenci.core.perms.forms import TendenciBaseForm
from addons.videos.embedly import is_pattern_match

class VideoForm(TendenciBaseForm):

    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'}, 
        mce_attrs={'storme_app_label':Video._meta.app_label, 
        'storme_model':Video._meta.module_name.lower()}))

    status_detail = forms.ChoiceField(choices=(('active','Active'),('pending','Pending')))

    clear_image = forms.BooleanField(required=False)

    class Meta:
        model = Video
        fields = (
            'title',
            'slug',
            'category',
            'image',
            'video_url',
            'tags',
            'description',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status',
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
        if not value:
            return value
        if not is_pattern_match(value):
            raise forms.ValidationError('This url is not supported by embed.ly')
        return value

    def save(self, *args, **kwargs):
        video = super(VideoForm, self).save(*args, **kwargs)
        if self.cleaned_data['clear_image']:
            video.image.delete()
        return video