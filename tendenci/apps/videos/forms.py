from datetime import datetime
from django import forms
from django.contrib.admin import widgets
from django.utils.translation import gettext_lazy as _

from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.videos.models import Video
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.perms.forms import TendenciBaseForm
from tendenci.apps.user_groups.models import Group
from tendenci.apps.perms.utils import get_query_filters, get_groups_query_filters
from .utils import get_embedly_client

class VideoForm(TendenciBaseForm):
    release_dt = forms.SplitDateTimeField(label=_('Release Date/Time'),
                                          input_date_formats=['%Y-%m-%d', '%m/%d/%Y'],
                                          input_time_formats=['%I:%M %p', '%H:%M:%S'])
    description = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':Video._meta.app_label,
        'storme_model':Video._meta.model_name.lower()}))

    status_detail = forms.ChoiceField(choices=(('active', 'Active'),('pending', 'Pending')))

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
            'group',
            'description',
            'release_dt',
            'allow_anonymous_view',
            'user_perms',
            'group_perms',
            'member_perms',
            'status_detail',
        )
        fieldsets = (
            (None, {
                'fields': ('title', 'slug', 'category',
                           'video_type', 'image', 'clear_image',
                           'video_url', 'group', 'tags',
                           'description', 'release_dt')}),
            (_('Permissions'), {
                'fields': ['allow_anonymous_view',
                         'user_perms',
                         'member_perms',
                         'group_perms',
                         ],
              'classes': ['permissions'],
                      }),
            (_('Publishing Status'), {
                'fields': ('status_detail',)}),
        )

    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        self.embedly_403 = False
        self.fields['group'].queryset = Group.objects.filter(status=True,
                                    status_detail="active").order_by('name')
        if self.instance.pk:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['description'].widget.mce_attrs['app_instance_id'] = 0
        self.fields['release_dt'].widget = widgets.AdminSplitDateTime()
        self.fields['release_dt'].initial = datetime.now()

    def clean(self, *args, **kwargs):
        super(VideoForm, self).clean(*args, **kwargs)
        if self.embedly_403:
            if not self.cleaned_data.get('image'):
                raise forms.ValidationError('Please provide a thumbnail of your video in the image upload field.')
        return self.cleaned_data

    def clean_video_url(self):
        video_url = self.cleaned_data.get('video_url')

        if not video_url:
            raise forms.ValidationError('You must enter a URL')

        if self.instance and self.instance.video_url == video_url:
            # the video_url is not changed, let it go
            return video_url

        # Get embedded object from URL
        client = get_embedly_client()
        obj = client.oembed(video_url)
        if obj.get('error'):
            if obj.get('error_code') != 403:
                raise forms.ValidationError('This url is not supported by embed.ly')
            else:
                # if youbube video, we can get the thumbnail from youtube API
                if 'www.youtube.com' not in video_url:
                    self.embedly_403 = True
        return video_url

    def save(self, *args, **kwargs):
        video = super(VideoForm, self).save(*args, **kwargs)
        if self.cleaned_data['clear_image']:
            video.image.delete()
        return video


class VideoFrontEndForm(VideoForm):

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)
        super(VideoFrontEndForm, self).__init__(*args, **kwargs)

        self.fields['release_dt'].widget.attrs.update({'class': 'form-control'})

        # set queryset for the group field
        default_groups = Group.objects.filter(status=True, status_detail="active")
        if not self.request_user.is_superuser:

            if get_setting('module', 'user_groups', 'permrequiredingd') == 'change':
                filters = get_groups_query_filters(self.request_user,)
            else:
                filters = get_query_filters(self.request_user, 'user_groups.view_group', **{'perms_field': False})
            default_groups = default_groups.filter(filters).distinct()
        self.fields['group'].queryset = default_groups

        # status_detail
        if not self.request_user.is_superuser:
            self.fields.pop('status_detail')



class VideoSearchForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False, max_length=200,)
    cat = forms.CharField(required=False, max_length=200,)
    vtype = forms.CharField(required=False, max_length=200,)
